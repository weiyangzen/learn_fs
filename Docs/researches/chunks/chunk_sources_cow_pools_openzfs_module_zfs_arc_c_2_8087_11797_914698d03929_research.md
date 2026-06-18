# Chunk Research: sources/cow-pools/openzfs/module/zfs/arc.c lines 8087-11797

## Scope

This chunk starts inside `arc_init()` and covers ARC initialization tail, `arc_fini()`, the full explanatory comment and implementation core for L2ARC write/read/feed/rebuild/device lifecycle, exported ARC symbols, and ARC/L2ARC module parameters.

The first line is a continuation from the previous chunk: memory limit setup, `arc_c`, ARC metadata ratios, and `arc_dnode_limit` are established before line 8087. This chunk applies tunables, starts ARC/L2ARC services, then defines the L2ARC cache device machinery.

## APIs And Entry Points

- `arc_fini()` tears down low-memory hooks, flush task queues, ARC buffers, kstats, prune lists, eviction/reap threads, L2ARC free-on-write ABDs, buf caches, ARC state, and hotplug registration.
- L2ARC write/read callback path: `l2arc_write_done()`, `l2arc_untransform()`, `l2arc_read_done()`, and `l2arc_blk_fetch_done()` complete device I/O, update headers/statistics, validate checksums, decrypt/decompress as needed, and fall back to primary storage on bad L2ARC reads.
- L2ARC feed path: `l2arc_feed_thread()`, `l2arc_write_size()`, `l2arc_get_write_rate()`, `l2arc_dwpd_rate_limit()`, `l2arc_evict()`, `l2arc_write_buffers()`, and `l2arc_write_sublist()` select ARC buffers, evict overwrite regions, issue physical writes, and regulate feed interval/rate.
- L2ARC device lifecycle APIs: `l2arc_add_vdev()`, `l2arc_remove_vdev()`, `l2arc_rebuild_vdev()`, `l2arc_vdev_present()`, `l2arc_vdev_get()`, `l2arc_init()`, `l2arc_fini()`, `l2arc_spa_rebuild_start()`, and `l2arc_spa_rebuild_stop()`.
- Persistent L2ARC rebuild helpers: `l2arc_rebuild_dev()`, `l2arc_dev_rebuild_thread()`, `l2arc_rebuild()`, `l2arc_dev_hdr_read()`, `l2arc_log_blk_read()`, `l2arc_log_blk_restore()`, `l2arc_hdr_restore()`, `l2arc_log_blk_fetch()`, `l2arc_log_blk_fetch_abort()`, `l2arc_dev_hdr_update()`, `l2arc_log_blk_commit()`, `l2arc_log_blkptr_valid()`, `l2arc_log_blk_insert()`, and `l2arc_range_check_overlap()`.
- Pool-position marker helpers: `l2arc_get_list()`, `l2arc_sublist_lock()`, `l2arc_pool_has_devices()`, `l2arc_pool_markers_init()`, `l2arc_pool_markers_fini()`, `l2arc_get_state_size()`, `l2arc_flag_pass_reset()`, and `l2arc_reset_all_markers()`.
- Public integration at the end exports `arc_buf_size`, `arc_write`, `arc_read`, `arc_buf_info`, `arc_getbuf_func`, `arc_buf_destroy`, `arc_add_prune_callback`, and `arc_remove_prune_callback`; module params expose ARC sizing, eviction, prefetch, dnode, compression, and L2ARC feed/rebuild/endurance controls.

## Control Flow

ARC initialization tail applies tunings, clamps debug builds to a smaller target, registers hotplug handlers, initializes ARC states and buffer caches, creates prune/flush task queues, installs `arcstats`, starts eviction/reap zthreads, marks ARC cold, and derives `zfs_dirty_data_max`, `zfs_dirty_data_max_max`, and `zfs_wrlog_data_max` from memory/tunables. `arc_fini()` reverses this order carefully: it first stops low-memory and async flush activity, flushes all ARC buffers, deletes kstats and prune state, cancels zthreads, frees pending L2ARC ABDs before aggsums disappear, then runs `buf_fini()` before `arc_state_fini()` to avoid callbacks into freed ARC state.

L2ARC feed is per device. `l2arc_feed_thread()` sleeps until the next scheduled feed, exits if signaled or if the vdev is dead, takes `SCL_L2ARC` as reader, aborts under low-memory/header pressure, computes a target write size/rate, evicts the next overwrite span, writes selected buffers, adjusts the next interval based on actual bytes written, and releases the spa config lock.

Write selection prefers metadata and MFU before MRU data through `l2arc_get_list()`. `l2arc_write_buffers()` decides whether to use persistent per-pool markers based on total L2ARC capacity, resets markers after enough cumulative writes or scan depth, optionally skips metadata after repeated metadata-only cycles, round-robins multilists, and protects each sublist with busy flags so multiple L2ARC device threads avoid scanning the same sublist. `l2arc_write_sublist()` uses either persistent markers or head/tail scanning depending on ARC warmness, skips locked/ineligible buffers, bounds scan headroom, applies copy/compress/encrypt transforms if the L2ARC write cannot directly use the ARC ABD, records L2ARC metadata on the header, queues writes under a root zio, and periodically commits L2ARC log blocks.

Write completion in `l2arc_write_done()` walks headers inserted after a dummy head marker, retries when hash locks are unavailable to avoid leaving `ARC_FLAG_L2_WRITING` set, drops failed L2ARC entries and log block pointers, restores device-header log pointers on failure, frees temporary log-block ABDs, removes the dummy head, updates vdev space for dropped bytes, drains device-specific free-on-write ABDs, and frees the callback.

Read completion in `l2arc_read_done()` copies temporary read buffers into real ARC storage when needed, rewrites the zio block pointer to the cached BP copy, validates checksum, decrypts/decompresses through `l2arc_untransform()` unless raw encrypted data is being used, and hands successful reads to `arc_read_done()`. Bad checksum, transform error, I/O error, or concurrent L2 eviction causes stats updates and fallback to primary storage; async fallbacks update existing ARC callbacks with the new zio head.

Eviction in `l2arc_evict()` handles rotary wraparound, optional TRIM ahead, persistent evict-hand recording, log-block pointer reclamation, L2-only header destruction, L1-cached L2 metadata destruction, and marking in-flight L2 reads as evicted. Wraparound resets write/evict hands and DWPD counters when the first sweep finishes.

Persistent rebuild starts when `l2arc_rebuild_dev()` accepts an on-disk device header and marks the device pending, or schedules whole-device TRIM/new header if rebuild cannot proceed on a writable pool. `l2arc_spa_rebuild_start()` launches one rebuild thread per eligible spa cache vdev after import; stop/remove paths set cancel flags and wait. `l2arc_rebuild()` restores device hands/trim state from the header, walks the two interleaved log-block chains with one-block lookahead I/O, aborts on memory pressure, validates loop/eviction boundaries, reconstructs L2-only ARC headers via `l2arc_log_blk_restore()` and `l2arc_hdr_restore()`, records restored log-block pointers/stats, and logs success, disabled, no-valid-blocks, cancellation, or abort outcomes.

Device add/remove is explicit. `l2arc_add_vdev()` allocates `l2arc_dev_t`, reserves space after labels/header, initializes lists/refcounts/DWPD/feed-thread fields, reads or initializes rebuild state before publishing the device, initializes per-pool markers for the first device, updates capacity counters, and starts a named per-device feed thread for writable pools. `l2arc_remove_vdev()` cancels rebuild, stops the feed thread, removes the device from the global list under `SCL_L2ARC` writer protection, updates pool capacity/markers, and either tears down synchronously or queues asynchronous teardown when the pool is exported/destroyed.

## State And Dependencies

Key global/module state touched includes `arc_c`, `arc_c_min`, dirty/write-log maxima, `arc_warm`, `arc_stats`, ARC prune/flush task queues, eviction/reap zthreads, `l2arc_dev_list`, `l2arc_ndev`, `l2arc_free_on_write`, rebuild locks/CVs, and module tunables such as `l2arc_write_max`, `l2arc_dwpd_limit`, `l2arc_headroom`, `l2arc_meta_cycles`, `l2arc_ext_headroom_pct`, `l2arc_trim_ahead`, and `l2arc_rebuild_enabled`.

Per-device state mutated includes `l2ad_spa`, `l2ad_vdev`, `l2ad_start/end/hand/evict`, `l2ad_first`, `l2ad_writing`, `l2ad_trim_all`, DWPD counters, feed-thread flags/CV/lock, `l2ad_buflist`, log-block pointer list, log block assembly fields, allocation/log-block refcounts, `l2ad_rebuild*` flags, and the in-memory persistent device header.

Per-pool state under `spa->spa_l2arc_info` includes marker arrays for each feed pass/sublist, sublist busy/reset flags, next-sublist cursors, extended scan counters, total/smallest L2ARC capacity, and cumulative writes used to reset marker depth.

Dependencies span ARC header/list/refcount helpers, multilist sublists, ABD allocation/copy/free, ZIO physical read/write/root/wait, SPA config locks, vdev space accounting and TRIM, crypto key lookup and ABD encryption/decryption, compression/decompression, Fletcher checksums, kstats/history/debug logging, kernel thread/CV/mutex APIs, taskqs, and module-parameter registration macros.

## Risks And Cross-Chunk References

- This chunk begins mid-`arc_init()`; the function prologue, ARC sizing defaults, low-memory initialization, and parameter setter definitions are in chunk 1.
- Many L2ARC helpers rely on types, flags, tunables, stats, macros, and small helpers defined earlier in `arc.c`, including `arc_buf_hdr_t`, `l2arc_dev_t`, `l2arc_log_blk_phys_t`, `HDR_*`, `ARCSTAT_*`, `l2arc_free_abd_on_write()`, `arc_hdr_l2hdr_destroy()`, and log-block property macros.
- Lock ordering is delicate: several paths use `mutex_tryenter(HDR_LOCK())` while holding `l2ad_mtx` to avoid deadlock with writer selection; missed locks cause retries and stats bumps.
- `l2arc_write_done()` must always clear `ARC_FLAG_L2_WRITING`; failed lock acquisition paths deliberately reinsert the dummy head to resume where they left off.
- Temporary transformed ABDs are queued for free-on-write and drained after zio completion. Missing this would risk either use-after-free during physical writes or leaked ABDs.
- Persistent marker logic is shared across per-device feed threads; incorrect busy/reset flag handling could skip sublists indefinitely or cause repeated scanning of hot areas.
- DWPD rate limiting treats first-pass writes specially and resets at device wrap; capacity or time arithmetic errors could over-throttle or overrun endurance budgets.
- Persistent rebuild intentionally restores possibly stale L2-only headers; correctness depends on DVA plus birth TXG validation in ARC read paths outside this chunk.
- Rebuild cancellation depends on `l2arc_rebuild_thr_lock`/CV and spa config lock retry loops. Remove/export paths must set cancel before tearing down device memory.
- `l2arc_log_blkptr_valid()` and `l2arc_range_check_overlap()` encode rotary-buffer validity; off-by-one errors here can restore overwritten log blocks or discard valid ones.
- The exported symbols and module parameters integrate earlier ARC APIs and tunables with kernel/module users; several setter callbacks are declared outside this chunk.

## Summary

This chunk is the L2ARC operational core of OpenZFS ARC: it completes ARC startup/shutdown, implements per-device L2ARC feeding, write completion, read fallback, rotary eviction, persistent metadata logging, import-time rebuild, device add/remove, and exposes the relevant ARC/L2ARC tunables. The highest-risk areas are concurrency and lifetime management around ARC header locks, per-device lists, asynchronous zios, persistent rebuild cancellation, and rotary address validation.