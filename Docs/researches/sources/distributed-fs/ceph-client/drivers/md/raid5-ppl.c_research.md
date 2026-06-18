# sources/distributed-fs/ceph-client/drivers/md/raid5-ppl.c

## Purpose

`raid5-ppl.c` implements the Linux MD RAID5 Partial Parity Log (PPL), a distributed consistency mechanism for closing the RAID5 write hole without a dedicated journal device. Each member disk owns a PPL area, and writes for a stripe are logged to the PPL stored on the stripe's parity disk before the actual data and parity writes are released to RAID5.

The logged record is not a full data journal. It stores a 4 KiB `struct ppl_header` followed by partial parity pages for the logged stripes. A header entry identifies the affected RAID data range, parity disk, data length, partial parity length, and checksum. Full-stripe writes log only metadata that lets recovery recalculate parity from all data disks; partial-stripe writes additionally log one page of partial parity per affected stripe. On unclean start, recovery replays valid PPL entries by reading modified data chunks, xoring them with logged partial parity when present, and writing the reconstructed parity block.

## Important APIs, Types, and Functions

Core private types:

- `struct ppl_conf`: per-array PPL state stored in `r5conf->log_private`; owns the child logs, log sequence counter, bio sets, io-unit mempool, recovery counters, retry list for no-memory stripes, block size, and array signature.
- `struct ppl_log`: per-member-disk log state; points at the associated `md_rdev`, serializes submission with `io_mutex`, tracks `current_io`, all pending `ppl_io_unit`s, next PPL sector for multiple-PPL mode, usable entry space, write-cache state, and the bitmap of disks that need cache flushes before the next io-unit can complete.
- `struct ppl_io_unit`: one persisted PPL write. It owns the header page, entry count, accumulated partial-parity size, sequence number, stripe list, pending stripe and flush counters, and an inline bio with inline bvecs.

On-disk structures come from `include/uapi/linux/raid/md_p.h`:

- `struct ppl_header_entry`: packed entry with `data_sector`, `pp_size`, `data_size`, `parity_disk`, and `checksum`.
- `struct ppl_header`: packed 4 KiB header with reserved bytes filled with `0xff`, signature, generation, entry count, header checksum, and `PPL_HDR_MAX_ENTRIES` entries.

Primary exported hooks declared in `raid5-log.h`:

- `ops_run_partial_parity()`: async_tx operation used by RAID5 reconstruction code to populate `sh->ppl_page`.
- `ppl_init_log()` / `ppl_exit_log()`: enable and tear down PPL for a RAID5 array.
- `ppl_write_stripe()` / `ppl_write_stripe_run()`: trap eligible stripes into PPL and submit current io-units.
- `ppl_stripe_write_finished()`: complete a PPL io-unit after logged stripes finish writing to the array.
- `ppl_modify_log()`: add or remove a member disk from PPL tracking.
- `ppl_quiesce()`: wait until submitted io-units drain.
- `ppl_handle_flush_request()`: special handling for flush bios while PPL is enabled.
- `ppl_write_hint`: sysfs attribute placeholder that validates writes but currently reports `0` and does not store a meaningful hint.

Important internal helpers:

- `ppl_log_stripe()`: groups a stripe into the current io-unit, creates/appends header entries, accumulates data/partial-parity sizes, and updates per-entry CRC.
- `ppl_submit_iounit()`: finalizes entries and header checksum, builds the log bio chain, advances multi-PPL write position, and records which data disks require flushes.
- `ppl_log_endio()`: handles PPL write completion, marks log errors with `md_error()`, and releases trapped stripes back to RAID5 handling.
- `ppl_io_unit_finished()`: removes an io-unit from the log list, frees it, retries one no-memory stripe, and wakes quiesce waiters.
- `ppl_do_flush()` / `ppl_flush_endio()`: issue and complete `REQ_PREFLUSH` bios for disks with write-back caches that participated in the logged write.
- `ppl_load_distributed()`, `ppl_recover()`, and `ppl_recover_entry()`: scan persisted log headers, validate checksums/signatures, replay entries for dirty startup, and clear the log with an empty header.
- `ppl_validate_rdev()` and `ppl_init_child_log()`: validate PPL placement/size and initialize per-disk log geometry.

## Control Flow

Initialization starts through `log_init(conf, journal_dev, raid5_has_ppl(conf))` in `raid5.c`, which dispatches to `ppl_init_log()` when no journal device is configured and the array has PPL enabled. `ppl_init_log()` rejects unsupported configurations: non-4 KiB page size, non-RAID5 level, bitmap use, journal use, or an array too wide for `disk_flush_bitmap`. It allocates `ppl_conf`, initializes the io-unit mempool and bio sets, creates one `ppl_log` per RAID disk, validates each present rdev's PPL area, and loads/replays existing logs. Only after successful load does it publish `conf->log_private` and set `MD_HAS_PPL`.

During normal writes, RAID5 allocates `sh->ppl_page` for each stripe when PPL is enabled. The RAID5 operation scheduler sets `STRIPE_OP_PARTIAL_PARITY` for eligible partial writes after `STRIPE_OP_BIODRAIN` is requested and the parity device is in sync. `raid5_run_ops()` then calls `ops_run_partial_parity()` between prexor and biodrain. In read-modify-write mode, it copies the precomputed parity page into `sh->ppl_page`; in reconstruct-write mode, it xors up-to-date non-updated data pages. This page becomes the persisted partial parity for recovery.

The generic log hook `log_stripe()` dispatches to `ppl_write_stripe()`. That function declines sync stripes, missing PPL pages, non-parity writes, or out-of-sync parity with `-EAGAIN`; otherwise it selects the child log indexed by `sh->pd_idx`, sets `STRIPE_LOG_TRAPPED`, clears `STRIPE_DELAYED`, takes a stripe reference, and calls `ppl_log_stripe()`. If no io-unit can be allocated, the stripe is placed on `ppl_conf->no_mem_stripes` for later retry while still trapped.

`ppl_log_stripe()` appends to the current io-unit unless it is full by partial-parity byte space or `PPL_HDR_MAX_ENTRIES`. It computes the first modified data sector and number of modified data disks. A stripe can be appended to the previous header entry only when it is the next stripe, stays within the same chunk group, and writes the same data-disk pattern; otherwise a new entry is opened. Full-stripe writes increase `data_size` but leave `pp_size` zero. Partial writes add one page to `pp_size`, increase `io->pp_size`, and update the running CRC with `sh->ppl_page`. The stripe is linked into `io->stripe_list` and `sh->ppl_io` points back to the io-unit.

`ppl_write_stripe_run()` iterates all child logs and calls `ppl_submit_current_io()`. The first unsubmitted io-unit on each log is marked submitted; if it was the current accepting unit, `current_io` is cleared. `ppl_submit_iounit()` converts recorded data sectors to the configured on-disk block units, finalizes entry checksums by complementing the running CRC, writes `entries_count` and header checksum, rewinds `next_io_sector` in multiple-PPL mode if needed, and submits a bio chain containing the header plus all partial-parity pages. Once `ppl_log_endio()` runs, the trapped stripes are released for actual RAID writes.

After the data/parity writes complete, RAID5 calls `log_stripe_write_finished()`, which dispatches to `ppl_stripe_write_finished()`. The function clears `sh->ppl_io` and decrements the io-unit's pending stripe count. When all stripes have written, the io-unit either issues required disk flushes or is removed and freed immediately. Completion also wakes the RAID5 thread and `wait_for_quiescent` waiters.

## State and Persistence Behavior

PPL persistence is per parity disk. `ppl_write_stripe()` chooses `ppl_conf->child_logs[sh->pd_idx]`, so each stripe is logged on the same disk that will receive parity. This matches recovery, where `ppl_recover_entry()` asserts that the parity disk computed from the array sector matches `e->parity_disk` and the rdev backing the log.

The log region starts with a 4 KiB header. Single-PPL mode uses the configured PPL space after subtracting the header. Multiple-PPL mode is enabled when the rdev PPL area can hold at least two `(128 KiB data + 4 KiB header)` slots; the writer advances `next_io_sector` through the region and wraps when the next io-unit will not fit. Generations increase through `ppl_conf->seq`, and load scans headers until an invalid checksum/signature or decreasing generation identifies the latest valid PPL.

Checksums are central to crash safety. Each partial-parity entry checksum is computed incrementally while stripes are logged and stored as `~crc32c`. The header checksum is also stored as `~crc32c` over the 4 KiB header with checksum field cleared by construction before final assignment. Recovery validates the header first, then validates each entry's partial-parity payload before replaying that entry. A bad entry increments `mismatch_count` and is skipped while subsequent entries may still be attempted.

Dirty-start recovery occurs only before the personality is fully running (`!mddev->pers`) and when `resync_offset != MaxSector`. `ppl_recover()` walks entries and calls `ppl_recover_entry()` for checksum-valid ones. Recovery reads the affected data blocks from in-sync data member disks, optionally xors the corresponding logged partial parity, and writes the resulting parity block. After recovery, `ppl_recover()` flushes the parity log disk cache. `ppl_load_distributed()` writes an empty header when starting the array, clearing old PPL state. If recovery succeeds cleanly and entries were recovered, `ppl_init_log()` can mark a dirty array clean by setting `resync_offset = MaxSector` and `MD_SB_CHANGE_CLEAN`.

Write-back cache ordering is handled at io-unit completion. While building the PPL bio, `ppl_submit_iounit()` records any member disk with write cache enabled and `R5_Wantwrite` set in `disk_flush_bitmap`. After all logged stripes have completed, `ppl_do_flush()` issues `REQ_PREFLUSH` to those disks. This prevents the next io-unit from being submitted before previous data/parity writes are durable enough for the log ordering model.

## Dependencies and Integration Points

The file depends heavily on MD RAID5 internals: `struct r5conf`, `struct stripe_head`, per-device `R5_*` flags, `STRIPE_*` state bits, `raid5_compute_sector()`, `raid5_release_stripe()`, and the generic log dispatch helpers in `raid5-log.h`. `raid5.c` integrates PPL by disabling stripe batching when PPL is active, allocating `ppl_page` in stripe heads, setting `STRIPE_OP_PARTIAL_PARITY`, routing log hooks to PPL, and exposing `ppl_write_hint` in the RAID5 sysfs attributes.

Block-layer dependencies include `bio_init()`, `bio_alloc_bioset()`, `bio_chain()`, `submit_bio()`, `sync_page_io()`, `blkdev_issue_flush()`, and `blkdev_issue_zeroout()`. PPL uses `REQ_FUA` for log writes, `REQ_PREFLUSH` for cache flushes, and synchronous page I/O during recovery and empty-header writes.

Async data movement uses `async_memcpy()` and `async_xor()` through the async_tx API. CRC validation uses `crc32c`. Memory lifetime depends on `kmem_cache`, `mempool`, `bioset`, and per-stripe `struct page` allocation.

Metadata dependencies include `md_rdev->ppl.{sector,size,offset}`, `md_rdev->data_offset`, superblock size, external metadata mode, `mddev->uuid`, `mddev->resync_offset`, `mddev->flags`, and `mddev->sb_flags`. For native metadata, the PPL signature is derived from the array UUID; for external metadata, signatures are accepted from disk but must be consistent across member disks.

## Risks and Edge Cases

- PPL is intentionally narrow: `ppl_init_log()` only supports RAID5, 4 KiB pages, no bitmap, no journal, and arrays no wider than `disk_flush_bitmap`.
- A PPL area that is too small, overlaps data, or overlaps native superblock metadata causes initialization or member addition failure.
- Recovery is conservative about missing data devices. `ppl_recover_entry()` only updates parity when all modified data disks needed for that block can be read; read/write failures call `md_error()` and abort recovery.
- Header or entry checksum mismatch does not necessarily fail the whole scan immediately. Bad headers choose the previous valid PPL in multi-PPL scanning; bad entry payloads are skipped and counted. Enabling PPL on a running array rejects any mismatch.
- The append logic assumes each header entry describes consecutive stripe_heads with the same modified data-disk pattern. RAID5 write admission enforces this by treating non-consecutive data chunks within a stripe as an overlap when PPL is enabled.
- `ppl_write_stripe()` can leave stripes on `no_mem_stripes` after allocation failure; progress depends on `ppl_io_unit_finished()` retrying one deferred stripe when an io-unit is freed.
- `ppl_log_endio()` releases trapped stripes even after log write failure, after marking the log rdev faulty. Callers must rely on MD error handling to prevent unsafe continuation.
- The write-cache flush bitmap is stored in `unsigned long`, so disk-count support is architecture-width constrained and validated during init.
- `ppl_handle_flush_request()` completes zero-length flushes immediately and strips `REQ_PREFLUSH` from non-empty bios, relying on PPL's own ordering rather than passing arbitrary flushes through unchanged.

## Test Signals

Useful validation signals for this file include:

- Create/start RAID5 arrays with `consistency_policy=ppl`, verify successful `ppl_init_log()`, `MD_HAS_PPL`, per-stripe `ppl_page` allocation, and rejection of unsupported combinations such as bitmap, journal, RAID6, too-small PPL space, and overlapping PPL metadata.
- Exercise partial-stripe and full-stripe writes, then confirm `ppl_log_stripe()` creates entries with expected `data_size`, `pp_size`, parity disk, and CRC behavior. Full-stripe writes should log entries with `pp_size == 0`.
- Force io-units to fill by entry count or partial-parity space and verify sequential submission, `current_io` rotation, and multiple-PPL `next_io_sector` wrap behavior.
- Run with write-back cache enabled on member disks and verify `disk_flush_bitmap`, `ppl_do_flush()`, and delayed `ppl_io_unit_finished()` ordering.
- Inject PPL bio failures, data read failures during recovery, parity write failures, and flush failures; expected signals are `md_error()` calls, recovery errors, or skipped entries with mismatch counters.
- Simulate unclean shutdown after PPL log write but before data/parity completion. On restart, valid entries should increment `recovered_entries`, repair parity, flush the log disk, write an empty header, and potentially mark the array clean when no mismatch occurred.
- Corrupt header checksum, signature, generation sequence, or partial-parity payload and verify scan fallback, mismatch counting, running-array enable rejection, and no replay of checksum-invalid entries.
- Validate member add/remove through `ppl_modify_log()`: addition should validate PPL space, write an empty header, and initialize child log state; removal should null the rdev under the log mutex.
