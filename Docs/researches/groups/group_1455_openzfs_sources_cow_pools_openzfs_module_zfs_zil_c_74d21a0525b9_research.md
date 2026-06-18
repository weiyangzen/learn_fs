# Group Research: group_1455_openzfs_sources_cow_pools_openzfs_module_zfs_zil_c_74d21a0525b9

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/openzfs`.  
Files read completely: `zil.c` 4907 lines.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zil.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zil.c

## Purpose
Implements the OpenZFS ZFS Intent Log (ZIL): per-dataset synchronous intent logging, log block allocation and writeback, crash claiming/replay/destruction, in-memory intent transaction queues, commit waiters, LWB lifecycle, and ZIL module statistics/tunables.

## Main Responsibilities
- Parses on-disk ZIL chains and validates log block sequence/checksum linkage.
- Reads ZIL log blocks and indirect write data through ARC, including raw/decrypt behavior.
- Claims or frees ZIL blocks during pool import, checkpoint rewind, replay, destroy, and sync.
- Manages in-memory intent transactions (`itx_t`) across per-txg sync and async queues.
- Chooses write logging mode: copied data, need-copy data, or indirect block pointers.
- Allocates, opens, closes, fills, issues, flushes, and frees Log Write Blocks (`lwb_t`).
- Preserves commit ordering through `zio` dependency graphs and per-LWB waiter lists.
- Implements `zil_commit()` semantics using synthetic `TX_COMMIT` records and commit waiters.
- Handles ZIL suspension, crash fallback, restart cleanup, and sync-time header updates.
- Replays claimed ZIL records into filesystem/zvol replay vectors.
- Publishes global and per-zilog ZIL kstats and module parameters.

## Key Data And State
- Tunables:
  - `zfs_commit_timeout_pct`: timeout used before an open LWB is forced closed for a waiting commit.
  - `zil_replay_disable`: global replay-disable switch.
  - `zil_nocacheflush`: disables post-write vdev flushes, unsafe across power loss.
  - `zil_slog_bulk`: bulk SLOG sync-write priority threshold.
  - `zil_maxblocksize`, `zil_maxcopied`, `zfs_immediate_write_sz`, `zil_special_is_slog`: log block sizing and write-mode policy controls.
- `zil_stats`, `zil_sums_global`, `zil_kstats_global`: named kstat wiring for commit counts, ITX modes, SLOG/normal allocation/write accounting, errors, stalls, suspends, and crash fallback.
- `zilog_t`: owns the per-objset ZIL header pointer, LWB lists, crash list, per-txg ITX queues, commit list, locks/CVs, replay state, suspension/restart state, latency/history prediction state, and kstat sums.
- `lwb_t`: in-memory representation of one ZIL log block with state, block pointer, buffer, ITX list, waiter list, vdev flush tree, zio handles, txg bounds, and allocation/write metadata.
- `zil_commit_waiter_t`: condition-variable object attached to a synthetic commit ITX until it is linked to an LWB or skipped.
- AVL helpers:
  - `zl_bp_tree` deduplicates block pointers during parsing/claim/free.
  - `lwb_vdev_tree` tracks top-level vdevs that need cache flushes after LWB writes.
  - async ITX trees group asynchronous records by object id.

## Important Functions
- `zil_read_log_block()`: reads one ZIL block, validates sequence/checksum linkage and `zc_nused`, handles slim `ZIO_CHECKSUM_ZILOG2` vs legacy layout, and returns record bounds plus the next block pointer.
- `zil_read_log_data()`: reads `TX_WRITE` indirect data, verifies raw data when no replay buffer is needed, and zero-fills holes.
- `zil_parse()`: walks the log chain from `zh_log`, invokes block and record callbacks, stops at claim sequence limits or corruption, and records parse progress counters.
- `zil_claim()`: import-time claim path. Clears invalid checkpoint/SPA_LOG_CLEAR logs, claims readable log blocks and write data, records highest claimed block/record sequence, and marks replay needed.
- `zil_check_log_chain()`: verifies claimability without modifying ownership, skipping invalid removed/faulted log vdev cases and checkpoint-unclaimed logs.
- `zil_destroy()` / `zil_destroy_sync()`: tears down a ZIL chain, optionally retaining the first block for fast later creation, and schedules sync-time frees/header clearing.
- `zil_create()`: creates the initial on-disk ZIL chain block if needed, activates `zilsaxattr` when appropriate, allocates the first LWB, and waits for header persistence.
- `zil_alloc_lwb()` / `zil_free_lwb()`: allocate/free in-memory LWBs and link/unlink them from the zilog.
- `zil_lwb_write_open()`, `zil_lwb_write_close()`, `zil_lwb_write_issue()`: core LWB pipeline. Open allocates the buffer, close predicts/allocates the next LWB shell, issue fills records, creates write/root zios, allocates the next on-disk block pointer, sets zio dependencies, updates stats, and submits IO.
- `zil_lwb_write_done()` / `zil_lwb_flush_vdevs_done()`: post-write and post-flush completion callbacks. They free buffers, optionally defer flushes to a later LWB, signal commit waiters, destroy committed ITXs, update latency, and maintain inflight txg counters.
- `zil_lwb_assign()`: assigns ITXs to LWBs, splits large `WR_NEED_COPY` writes across log blocks, creates log sequence numbers, and closes full LWBs.
- `zil_lwb_commit()`: copies an ITX record into an LWB buffer, fetches write data or indirect block pointers through `zl_get_data`, updates statistics, and falls back to txg sync on data fetch failures.
- `zil_write_state()`: selects `WR_INDIRECT`, `WR_COPIED`, or `WR_NEED_COPY` based on logbias, O_DIRECT, size, blocksize, SLOG/special vdev availability, and whether the operation will commit immediately.
- `zil_itx_create()`, `zil_itx_clone()`, `zil_itx_destroy()`, `zil_itx_assign()`: allocate, split, free, and queue intent transactions in per-txg sync or async structures.
- `zil_async_to_sync()` / `zil_remove_async()`: promote or remove asynchronous object-scoped records, used for fsync-like commits and rename ordering.
- `zil_get_commit_list()`, `zil_prune_commit_list()`, `zil_process_commit_list()`, `zil_commit_writer()`: move queued ITXs into the commit list, optimize pure commit waiters, assign records to LWBs, and issue closed LWBs.
- `zil_commit_waiter()` / `zil_commit_waiter_timeout()`: wait for commit completion and force an open LWB closed after the adaptive timeout.
- `zil_commit_flags()` / `zil_commit_impl()`: public commit path. Handles disabled sync, read-only pools, suspended/crashed ZIL fallback, synthetic commit ITX creation, writer/waiter coordination, failmode behavior, and txg-sync fallback on errors.
- `zil_crash()` / `zil_crash_clean()`: abandon the current ZIL pipeline after suspension/ESHUTDOWN paths, error all pending ITXs/waiters, zero the header in syncing context, and defer LWB cleanup until safe txgs.
- `zil_sync()` / `zil_clean()`: syncing-context cleanup. Waits for LWB IO for the txg, advances replay sequence, updates or clears the ZIL header, frees stable LWBs, and cleans synced ITX groups asynchronously.
- `zil_suspend()` / `zil_resume()` / `zil_reset()`: temporarily suspend a dataset ZIL, force all ZIL data to main pool, destroy the on-disk log, maintain long holds/key mappings, and resume later.
- `zil_replay()` / `zil_replay_log_record()` / `zil_replaying()`: replay claimed log records, skip already replayed or already committed records, fetch write payloads, invoke per-txtype replay vectors, update replay sequence, destroy the log, and mark replaying transactions.
- `zil_alloc()`, `zil_free()`, `zil_open()`, `zil_close()`, `zil_init()`, `zil_fini()`: lifecycle and module-cache/kstat setup.

## Control Flow Notes
- On-disk ZIL is a per-dataset linked list: the dataset header points at the first log block; each block contains records and a pointer/checksum seed for the next block.
- `zil_commit()` does not directly wait for a specific user ITX. It creates a synthetic `TX_COMMIT` ITX with a waiter, queues it after existing records, and returns when the LWB containing/skipping that waiter is stable.
- Sync ITXs preserve insertion order globally. Async ITXs preserve order per object and are promoted to sync for `zil_commit(foid)` or all objects for `foid == 0`.
- LWB completion order is enforced by making newer root zios depend on older root zios. When flushes are deferred, newer write zios may also depend on older write zios so flushes cannot precede the data they must stabilize.
- Open LWBs are intentionally held briefly for aggregation. More ZIL activity may fill and close them; otherwise the waiter timeout closes and issues them.
- Log block allocation is predictive. The code tracks recent burst sizes and current burst state to size future LWBs without always consuming maximum log space.
- Slim ZIL blocks use `ZIO_CHECKSUM_ZILOG2` and place the chain header at the front, allowing writes to shrink to the actually used size.
- Claim and replay sequence fields protect against replaying beyond the part of the log successfully claimed during import.
- `zil_sync()` is responsible for making the ZIL header point to the correct remaining chain head and freeing LWBs that are stable and old enough.
- During suspension, normal `zil_commit()` would bypass ZIL and wait for txg sync, so `zil_suspend()` calls `zil_commit_impl()` directly to flush already-open/ready LWBs first.

## Error Handling And Invariants
- Log parsing rejects malformed record lengths, record overruns, bad block sequence/checksum linkage, and invalid used-size fields.
- Claiming verifies indirect write data before claiming its block pointer; unreadable future data terminates usable log state rather than replaying unsafe records.
- Clone-range claim checks referenced blocks are allocated and not from the future before adding BRT references.
- Block pointer AVL deduplication prevents duplicate frees/claims while walking logs and write records.
- LWB freeing asserts no live child/write/root zios, empty ITX/waiter lists, empty vdev flush tree, and txg bounds no later than syncing txg.
- `zil_lwb_commit()` treats unexpected `zl_get_data()` errors as reason to fall back to txg sync; `ESHUTDOWN` crashes the ZIL and requires callers to abort use of affected LWBs/ITXs.
- Allocation failure for the next LWB stalls the ZIL writer until current LWBs sync, preventing a disconnected next block from leaking after crash.
- `zil_commit_flags()` returns `EIO` for continue/direct failmode handling after `ESHUTDOWN`; otherwise it blocks until the pool returns and treats eventual txg sync as success.
- Snapshots must not be dirtied or committed through ZIL; commit and dirty paths assert against snapshot mutation.
- Replay skips records already replayed (`zh_replay_seq`) or already committed before claim txg, validates transaction type, and ignores out-of-order records whose objects disappeared.
- ZIL crash cleanup avoids freeing blocks in the same or earlier txg than allocation/update, deferring through dirtying future txgs.
- `zil_close()` waits for relevant dirty, allocation, max ITX, and issued txgs before clearing `zl_get_data` and freeing the remaining unused LWB.

## Dependencies
Strongly coupled to OpenZFS storage and dataset internals: ARC reads, ZIO allocation/write/flush graphs, SPA/vdev state, DMU transactions and objsets, DSL datasets/pools/features, metaslab allocation checks, BRT clone-reference accounting, ZAP/dnode replay consumers, txg synchronization, taskqs, kernel kstats, AVL/list primitives, and encryption/raw-read behavior.

## Research Notes
This file is the ZIL durability engine. The highest-risk areas are commit waiter ordering, LWB state transitions, flush deferral dependencies, fallback behavior during pool suspension, allocation failure handling, and import/replay sequence boundaries. Changes here need careful reasoning about three timelines at once: in-memory ITX ordering, on-disk ZIL chain linkage, and txg sync/free ordering.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zil.c -->