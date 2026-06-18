# File Research: sources/cow-pools/openzfs/module/zfs/dsl_scan.c

## Role

Implements OpenZFS pool scan machinery: scrub, resilver, error scrub, async destroy block freeing, obsolete-block marking, scan checkpointing, sorted scrub I/O queues, scan progress accounting, and scan state persistence in the MOS pool directory.

## Major Subsystems

- Scan lifecycle:
  - `dsl_scan_init()` loads persisted scan and error-scrub state, handles old scrub layout compatibility, reloads the dataset queue, initializes DDT walks, and restores progress counters.
  - `dsl_scan_setup_check()` and `dsl_scan_setup_sync()` start scrub or resilver state, create the scan queue object, reset stats, initialize DDT traversal, emit events, and persist `dsl_scan_phys_t`.
  - `dsl_scan()` is the public start/resume entry point for scrub, resilver, and error scrub.
  - `dsl_scan_done()` tears down scan queues, removes legacy scrub keys, updates DTLs, rotates error logs, emits finish/cancel events, and marks scan state finished or canceled.
  - `dsl_scan_cancel()` and scrub/error-scrub pause/resume helpers wrap state changes in sync tasks.

- Error scrub:
  - `dsl_errorscrub_setup_sync()` initializes `errorscrub_phys`, cursor state, and event/history records.
  - `dsl_errorscrub_sync()` walks the last error log, reads affected blocks, supports both legacy bookmark names and `SPA_FEATURE_HEAD_ERRLOG`, limits blocks per txg, persists cursor state, and completes when no cursor entries remain.
  - `scrub_filesystem()` maps head error-log entries to live filesystems and relevant snapshots, then issues raw scrub reads for blocks still affected.
  - `read_by_block_level()` resolves a bookmark back to a current block pointer through dnode/dbuf lookup, avoids unloaded encrypted datasets, and issues scan I/O.

- Metadata traversal:
  - `dsl_scan_visit()` drives DDT traversal, MOS/origin traversal, resumed dataset traversal, and queued dataset traversal.
  - `dsl_scan_visitds()` scans one dataset’s root block, traverses its ZIL for live heads, adds next snapshots and clones to the queue, and handles repeated passes when mutation invalidates the current pass.
  - `dsl_scan_visitbp()`, `dsl_scan_recurse()`, and `dsl_scan_visitdnode()` recursively inspect block pointers, dnodes, objset blocks, indirect blocks, spill blocks, user/group/project accounting objects, and feature assertions.
  - Traversal skips holes, redacted blocks, blocks below `scn_cur_min_txg`, DDT-contained blocks already handled by the DDT pass, and physical births above `scn_cur_max_txg`.

- DDT scrub interaction:
  - `dsl_scan_ddt()` walks dedup-table classes up to `scn_ddt_class_max`.
  - `dsl_scan_ddt_entry()` creates synthetic block pointers for DDT entries and scans each physical variant once.
  - The file documents why DDT-scrub-first avoids repeatedly scrubbing deduped blocks but still tolerates class changes during an active scan.

- Sorted scan I/O:
  - `scan_io_t` stores the minimal block-pointer and bookmark data needed to reconstruct scrub/resilver reads.
  - Per-top-vdev `dsl_scan_io_queue_t` tracks queued `scan_io_t` records by address plus range extents by address and weighted size.
  - `dsl_scan_enqueue()` queues non-gang scan I/O into per-vdev sorted queues when sorted scans are active; gang blocks and legacy scans execute immediately.
  - `scan_io_queues_run()` fans out one worker per top-level vdev to issue queued extents.
  - `scan_io_queue_fetch_ext()` chooses LBA order during checkpoints or the best weighted extent during memory clearing.
  - `scan_io_queue_gather()` removes up to 32 queued I/Os from an extent at a time and shrinks/removes the extent.
  - `scan_exec_io()` applies global or per-vdev in-flight byte limits and issues raw scrub/resilver reads.
  - `dsl_scan_scrub_done()` releases ABD buffers, updates in-flight counters, wakes waiters, and increments scan or error-scrub errors.

- Prefetch:
  - `dsl_scan_prefetch_thread()` drains a bookmark-ordered prefetch queue under global scan in-flight limits.
  - `dsl_scan_prefetch()` queues metadata and indirect blocks likely to be needed by traversal.
  - `dsl_scan_prefetch_cb()` recursively schedules children from prefetched indirect, dnode, and objset blocks.
  - Prefetch is disabled for redacted blocks, holes, old births, and level-0 non-metadata data.

- Dataset mutation handling:
  - `dsl_scan_ds_destroyed()` updates active and cached bookmarks and removes/replaces dataset queue entries when datasets or snapshots are destroyed.
  - `dsl_scan_ds_snapshotted()` moves active scan references from a head to the newly created previous snapshot.
  - `dsl_scan_ds_clone_swapped()` swaps bookmarks and queue entries when clone promotion swaps dataset identities.
  - These paths use `SYNC_CACHED` persistence when the current on-disk scan state may not match in-core queue progress.

- Async destroy/free work:
  - `dsl_process_async_destroys()` frees blocks from `dp_free_bpobj`, async-destroy bptrees, and obsolete bpobjs before scrub/resilver work.
  - `dsl_scan_free_block_cb()` issues sync frees, updates the free dir accounting, waits periodically for async frees, and enforces per-txg limits.
  - Finished async destroy deactivates `SPA_FEATURE_ASYNC_DESTROY`, removes pool directory state, and handles leaked free-dir space when configured.

- Resilver integration:
  - `dsl_scan_need_resilver()` checks DTL coverage, gang/indirect special cases, and deferred-resilver state.
  - `dsl_scan_restart_resilver()` records restart txg.
  - `dsl_scan_assess_vdev()` requests or defers resilver when vdev DTL ranges require it.
  - `dsl_scan_sync()` restarts scans when needed for deferred resilver policy or explicit restart state.

## Main Sync Scheduler

`dsl_scan_sync()` is the primary syncing-context entry point. It only runs in sync pass 1, defers after import, processes async destroys first, handles scan restart conditions, applies test/debug suspension, optionally enables sorted scanning, decides whether to gather metadata or issue queued I/O, runs prefetch during traversal, waits for scan I/O roots, marks scan-complete txg, and persists state with `dsl_scan_sync_state()`.

For sorted scans, metadata traversal and queued I/O issuing are intentionally mutually exclusive. The scan gathers I/O until memory pressure or checkpointing triggers clearing, then issues sorted per-vdev extents until below the soft memory limit or until queues are empty.

## State and Synchronization

- Persistent state is stored in MOS ZAP entries `DMU_POOL_SCAN` and `DMU_POOL_ERRORSCRUB`.
- `scn_phys_cached` exists so dataset mutation can rewrite a safe cached scan state while sorted queues still contain unissued work.
- `scn_queues_pending` counts non-empty per-vdev scan queues.
- `spa_scrub_lock` protects global prefetch/scrub in-flight counters and prefetch queue coordination.
- Each top-level vdev has `vdev_scan_io_queue_lock` for its scan queue and per-vdev in-flight limits.
- `dp_config_rwlock` is entered while traversing pool/dataset topology.

## Tunables

The file defines module parameters for scan vdev in-flight limits, minimum per-txg times, suspend/progress controls, scrub I/O/prefetch disable switches, async free limits, scan memory limits, legacy scan mode, checkpoint interval, extent gap, fill weighting, resilver deferral policy, and error blocks per txg.

## Research Notes

This file is the core scrub/resilver engine. Its main complexity comes from making long-running traversal resumable while concurrently supporting copy-on-write dataset mutations, DDT dedup semantics, vdev DTL healing, async destroy cleanup, and physically sorted I/O issuance without persisting unsafe progress while queued reads remain outstanding.
