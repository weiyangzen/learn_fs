# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zvol_os.c

## Scope

Implements Linux-specific ZVOL block-device integration: BIO/request dispatch, blk-mq support, read/write/discard handling, open/release/ioctl operations, queue-limit setup, minor creation/removal/rename, disk capacity/read-only updates, and module initialization parameters.

## APIs And Behavior

- `zvol_request_impl()` validates block operations, rejects removed/read-only/bounds-violating I/O, acquires `zv_suspend_lock`, opens the ZIL lazily for writes, and dispatches reads/writes/discards either synchronously or through per-zvol taskqs.
- `zvol_write()`, `zvol_read()`, and `zvol_discard()` translate Linux BIO/request vectors to `zfs_uio_t`, use zvol range locks, call DMU read/write/free routines, update dataset/task I/O accounting, and honor flush/FUA or `ZFS_SYNC_ALWAYS` with `zil_commit()`.
- `zvol_mq_queue_rq()`, `zvol_blk_mq_alloc_tag_set()`, `zvol_submit_bio()`/`zvol_request()` bridge Linux block queue variants to the common request path.
- `zvol_open()` and `zvol_release()` manage first-open/last-close transitions, open-count state, read-only checks, media-change checks, and the `spa_namespace_lock` retry path needed to avoid vdev-on-zvol lock inversion.
- `zvol_ioctl()` supports `BLKFLSBUF` flushing/invalidation and `BLKZNAME` name copyout; geometry/revalidation helpers expose compatibility block-device behavior.
- `zvol_alloc()`, `zvol_alloc_non_blk_mq()`, and `zvol_alloc_blk_mq()` allocate `gendisk`, queue, blk-mq tag sets, queue limits, disk naming/minors, flags, range locks, and ZVOL state.
- `zvol_os_create_minor()` owns the Linux-side creation flow: allocate minor, own the DMU objset, read volume metadata, create state, replay/destroy ZIL as needed, prefetch blkid-probed regions, insert in the zvol table, and publish the disk.
- `zvol_os_remove_minor()`, `zvol_os_free()`, `zvol_os_rename_minor()`, `zvol_os_set_disk_ro()`, and `zvol_os_set_capacity()` handle teardown and visible disk state changes.
- `zvol_init()`/`zvol_fini()` call common zvol init/fini, register/unregister the block major, initialize blk-mq tunables, and manage the Linux `ida`.

## State And Dependencies

State centers on `zvol_state_t`, Linux `struct gendisk`, `request_queue`, optional `blk_mq_tag_set`, `zv_open_count`, `zv_suspend_lock`, `zv_state_lock`, `zv_rangelock`, `zv_zilog`, and `zv_zso`. It depends on Linux block APIs across many kernel compatibility variants, OpenZFS DMU/ZIL/dataset kstats/range locks, `spa_namespace_lock`, `ida`, taskqs, and queue-limit compatibility wrappers.

## Risks And Invariants

Lock ordering is critical: first/last open deliberately take `zv_suspend_lock` before `zv_state_lock`, and first open may need `spa_namespace_lock` despite Linux block-device locks already being held. Asynchronous taskq dispatch must always release `zv_suspend_lock` and complete the BIO/request exactly once. Minor creation becomes externally visible after `add_disk()`, so state insertion and objset disowning must be ordered carefully. Removal clears `private_data` before `del_gendisk()` and drops `zv_state_lock` around block-layer teardown to avoid deadlock.
