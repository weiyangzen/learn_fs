# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/arc.c lines 8414-10052

## Scope

This chunk covers illumos ZFS L2ARC write selection, feed-thread control, cache-device lifecycle, persistent L2ARC rebuild, log-block read/write/restore helpers, and rotary address validation. It starts mid-`l2arc_apply_transforms()`, so the earlier transform-entry decisions are in the previous chunk.

## APIs And Entry Points

- `l2arc_apply_transforms()` prepares aligned ABDs for L2ARC writes, including compression, encryption, padding, MAC verification, and cleanup on key/crypto failure.
- `l2arc_write_buffers()` scans ARC lists, selects eligible headers, writes buffers to an L2ARC vdev, logs persistent metadata, waits for write completion, and updates the device header.
- `l2arc_feed_thread()` periodically chooses an L2ARC device, evicts the overwrite range, writes buffers, and schedules the next feed.
- Device lifecycle: `l2arc_vdev_present()`, `l2arc_vdev_get()`, `l2arc_add_vdev()`, `l2arc_rebuild_vdev()`, `l2arc_remove_vdev()`.
- Subsystem lifecycle: `l2arc_init()`, `l2arc_fini()`, `l2arc_start()`, `l2arc_stop()`.
- Persistent rebuild: `l2arc_spa_rebuild_start()`, `l2arc_dev_rebuild_start()`, `l2arc_rebuild()`.
- Metadata I/O and restore helpers: `l2arc_dev_hdr_read()`, `l2arc_log_blk_read()`, `l2arc_log_blk_fetch()`, `l2arc_log_blk_fetch_abort()`, `l2arc_dev_hdr_update()`, `l2arc_log_blk_restore()`, `l2arc_hdr_restore()`, `l2arc_log_blk_commit()`, `l2arc_log_blkptr_valid()`, `l2arc_log_blk_insert()`, `l2arc_range_check_overlap()`.

## Control Flow

`l2arc_write_buffers()` iterates feed passes, optionally skipping MRU passes under `l2arc_mfuonly`. It locks ARC multilists, scans from head during cold ARC warmup and tail after warmup, bounds scan depth by headroom, uses `mutex_tryenter(HDR_LOCK())`, skips ineligible headers, marks chosen headers with `ARC_FLAG_L2_WRITING`, chooses either raw ABD, live ARC ABD, or transformed copy, then issues `zio_write_phys()` writes under one root zio.

The first selected write installs a dummy list marker for `l2arc_write_done()` cleanup. Each header gets `b_l2hdr` metadata, is inserted into `l2ad_buflist`, increments allocation refcounts, advances `l2ad_hand`, updates stats/vdev accounting, and is appended to the persistent log block. Full log blocks are committed immediately. If nothing is written, the dummy header is freed and the device header is updated only if eviction moved.

`l2arc_feed_thread()` waits on a timed CV, skips when no devices exist, obtains a device and spa config lock via `l2arc_dev_get_next()`, skips read-only pools, aborts on L2 header pressure, computes write size, calls `l2arc_evict()`, writes buffers, computes the next interval, and exits by resetting `l2arc_thread_exit`.

`l2arc_add_vdev()` allocates `l2arc_dev_t`, reserves label/header space, initializes hand/evict pointers, lists, refcounts, and device-header storage, publishes the device globally, and calls `l2arc_rebuild_vdev()`. `l2arc_rebuild_vdev()` computes log-entry count, reads the persistent device header, marks rebuild pending when valid, or writes a fresh zeroed header for writable pools.

`l2arc_rebuild()` restores hand/evict/first-pass state from the header, walks the persistent log-block chain with lookahead I/O, validates checksums/compression/magic, aborts under memory pressure, drops `SCL_L2ARC` while restoring headers, handles cancellation while reacquiring the config lock, records restored log-block pointers, and logs disabled/success/no-valid-blocks/canceled/aborted outcomes.

`l2arc_log_blk_restore()` restores entries in reverse order to preserve temporal ordering. `l2arc_hdr_restore()` allocates L2-only ARC headers, inserts them into device lists/refcounts, and handles duplicate cached headers by attaching missing L2 metadata to the existing header.

`l2arc_log_blk_commit()` serializes a full in-memory log block, links it into the previous-chain pointer, optionally LZ4-compresses it, updates `dh_start_lbps`, computes Fletcher-4, writes it at `l2ad_hand`, records the pointer/refcounts/stats, and resets log-block assembly fields.

## State And Dependencies

Key global state includes `l2arc_dev_list`, `l2arc_ndev`, `l2arc_dev_last`, `l2arc_thread_exit`, feed/rebuild locks and CVs, `l2arc_free_on_write`, `arc_warm`, `arc_c`, `arc_c_max`, `arc_meta_limit`, `astat_l2_hdr_size`, and tunables such as `l2arc_headroom`, `l2arc_meta_percent`, `l2arc_feed_secs`, and `l2arc_rebuild_enabled`.

Per-device state includes `l2ad_spa`, `l2ad_vdev`, `l2ad_start/end/hand/evict`, `l2ad_first`, `l2ad_writing`, rebuild flags, persistent header, buflist, log-block pointer list, log-block assembly fields, and allocation/log-block refcounts.

Dependencies include ARC header helpers, multilists, ABD APIs, ZIO physical I/O, SPA config locking, vdev accounting, compression/decompression, Fletcher checksums, byteswap helpers, DSL crypto key lookup/release, ABD encryption, zfs refcounts, kernel threads/CVs/mutexes, and ARC stat macros.

## Risks And Cross-Chunk References

- The chunk begins mid-`l2arc_apply_transforms()`; earlier copy/raw/shared-data decisions are in the previous chunk.
- `l2arc_write_buffers()` depends on earlier `l2arc_write_eligible()`, `l2arc_evict()`, `l2arc_write_done()`, and free-on-write ABD cleanup.
- `ARC_FLAG_L2_WRITING` is critical for header lifetime; completion must clear it on all success/failure paths.
- Direct ABD use is safe only when compression, encryption, sharing, and alignment flags are exactly right.
- Encrypted L2ARC writes intentionally skip buffers if the dataset key is unavailable.
- Rebuild drops `SCL_L2ARC` during header restoration, so cancellation/removal safety depends on rebuild locks and cancel flags.
- `l2arc_log_blkptr_valid()` and `l2arc_range_check_overlap()` are off-by-one-sensitive rotary-buffer checks.
- Restored L2-only headers are metadata; later ARC read paths must still validate DVA, birth, checksum, and transforms.

## Summary

This chunk is the illumos L2ARC operational core for writing cache-device data, persisting/restoring L2ARC metadata, managing cache vdev objects, and validating rotary log-block ranges. The highest-risk areas are asynchronous zio lifetime, ARC header locking, encryption/compression fidelity, rebuild cancellation, and wraparound address correctness.