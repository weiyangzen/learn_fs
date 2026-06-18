# sources/distributed-fs/lustre-release/lustre/llite/rw.c

## Purpose

`rw.c` implements Lustre llite shared page-cache read/write support across kernel versions. It owns client readahead budgeting, readahead pattern detection, readpage integration with CLIO, asynchronous readahead work, writeback submission through CLIO, and per-thread CLIO context lookup used by readpage/direct-I/O/write-begin code.

## Important APIs, types, and functions

Important exported functions are `ll_ra_count_put()`, `ll_ra_stats_inc()`, `ll_readahead_init()`, `ll_ras_enter()`, `ll_writepages()`, `ll_cl_find()`, `ll_cl_add()`, `ll_cl_remove()`, `ll_io_read_page()`, `ll_readpage()`, and optionally `ll_read_folio()`. Internal helpers include `ll_ra_count_get()`, `ll_read_ahead_page()`, `stride_page_count()`, `ria_page_count()`, `ras_align()`, `ll_read_ahead_pages()`, `ll_readahead_handle_work()`, `ll_readahead()`, `ll_readpages()`, `ras_reset()`, `ras_stride_reset()`, `ras_detect_read_pattern()`, `ras_update()`, `kickoff_async_readahead()`, and `ll_use_fast_io()`.

The file manipulates `struct ll_readahead_state`, `struct ll_ra_info`, `struct ra_io_arg`, `struct ll_readahead_work`, `struct ll_cl_context`, CLIO `struct cl_io`, `struct cl_page`, `struct cl_2queue`, `struct cl_read_ahead`, and VVP environment state.

## Control flow

Buffered reads enter `ll_readpage()` or `ll_read_folio()`. If the current thread has no `ll_cl_context`, the function attempts a fast cached-page path by finding an existing CLIO page, checking `cp_defer_uptodate`, updating readahead state on cache hit, optionally starting async readahead, marking the VM page uptodate, and unlocking it. If an active CLIO context exists, `ll_readpage()` validates truncation and lock coverage edge cases, asserts kernel readahead is disabled, handles direct-read fallback restart conditions, wraps the VM page in a CLIO page, and calls `ll_io_read_page()`.

`ll_io_read_page()` updates readahead state, queues the requested page if not already uptodate, optionally expands the queue with `ll_readahead()` or `ll_readpages()`, submits queued pages with `cl_io_submit_rw()`, waits for synchronous completion of the trigger page, discards unsent or temporary queue pages, and releases readahead locks.

Readahead policy starts with `ll_ras_enter()` when higher layers observe user read position and size. It tracks consecutive requests, whole-file-read eligibility, loose sequential reads, stride reads, and mmap cluster reads. `ras_update()` reacts to actual page hits/misses and grows or resets the window. `ll_readahead()` reserves global readahead budget, clamps to KMS/EOF, checks lock coverage with `cl_io_read_ahead_prep()`, queues pages, and advances `ras_next_readahead_idx`. `ll_readahead_handle_work()` performs the same work from a workqueue for async readahead.

Writeback enters `ll_writepages()`, maps kernel writeback reasons to CLIO fsync modes/priorities, skips freed/no-object inodes, calls `cl_sync_file_range()`, and updates `mapping->writeback_index` for cyclic or whole-file writeback.

## State and persistence behavior

The main persistent runtime state is in memory: per-superblock `ll_ra_info` tracks global and per-file readahead limits, current reserved pages, async queue, and stats; per-file `fd_ras` tracks window start, size, next index, RPC size, stride offsets, consecutive access counts, mmap range detection, and async last index. Page state is stored in CLIO pages and Linux page flags (`PageUptodate`, `cp_defer_uptodate`, `cp_ra_used`, `cp_ra_updated`). No durable on-disk state is written here; writeback delegates persistence to CLIO/OSC through `cl_sync_file_range()` and `cl_io_submit_rw()`.

## Dependencies and integration points

The file depends on llite internal inode/superblock/file structures, CLIO object/page/I/O APIs, VVP environment state, LNet/Lustre constants such as `PTLRPC_MAX_BRW_PAGES`, Linux page cache APIs, workqueues, writeback control, task I/O accounting, and lprocfs counters. It integrates with `rw26.c` through `ll_readpage()`, `ll_read_folio()`, `ll_writepages()`, and `ll_cl_find()`, with high-level read/write paths via `ll_cl_add()`/`ll_cl_remove()`, and with PCC mmap safeguards because PCC forces kernel readahead counters to zero before shared mapping use.

## Risks and edge cases

Readahead budget accounting is delicate: `ll_ra_count_get()` intentionally over-reserves minimum pages for performance, so callers must always return unused `ria_reserved`. Stride and mmap cluster detection can over-prefetch or reset too aggressively. The fast read path depends on valid CLIO page identity and layout assumptions. There are explicit workarounds for kernel 5.12 read batching adding an extra page, for truncated pages racing with lock cancellation, and for direct I/O falling back to buffered I/O under lockless mode. Kernel readahead must remain disabled; unexpected `ra_pages`/`io_pages` triggers assertions.

## Test signals

Relevant signals are lprocfs readahead stats (`RA_STAT_HIT`, `MISS`, `READAHEAD_PAGES`, `FORCEREAD_PAGES`, `ASYNC`, `EOF`, `MAX_IN_FLIGHT`, `FAILED_FAST_READ`, `MMAP_RANGE_READ`, `MISS_IN_WINDOW`), fast-read hit/miss behavior, async readahead inflight accounting, KMS/EOF clamping, stride read windows, mmap clustered faults, cyclic writeback index updates, direct-read fallback restart `-ENOLCK`, failpoints `OBD_FAIL_LLITE_READPAGE_PAUSE` and `OBD_FAIL_LLITE_READPAGE_PAUSE2`, and assertions that kernel readahead remains disabled.
