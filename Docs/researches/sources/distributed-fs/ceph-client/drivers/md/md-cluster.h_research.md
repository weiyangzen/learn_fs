# sources/distributed-fs/ceph-client/drivers/md/md-cluster.h

Purpose: Declares the MD cluster submodule interface consumed by MD core and cluster-aware personalities. It abstracts clustered coordination behind `struct md_cluster_operations` so the rest of MD can join/leave a cluster, coordinate metadata, synchronize recovery, and coordinate bitmap slots without depending on DLM internals.

Important APIs/types/functions: `struct md_cluster_operations` embeds `struct md_submodule_head` and provides callbacks for cluster lifecycle (`join`, `leave`, `slot_number`), resync coordination (`resync_start`, `resync_finish`, `resync_info_update/get`, `resync_start_notify`, `resync_status_get`, `area_resyncing`), metadata update serialization (`metadata_update_start/finish/cancel`, `update_size`), disk membership (`add_new_disk`, `add_new_disk_cancel`, `new_disk_ack`, `remove_disk`), and bitmap-slot coordination (`load_bitmaps`, `gather_bitmaps`, `resize_bitmaps`, `lock_all_bitmaps`, `unlock_all_bitmaps`). It also declares `md_setup_cluster()`, `md_cluster_stop()`, and `md_reload_sb()`.

Control flow: No executable logic lives here. MD code calls these operations through `mddev->cluster_ops` after the cluster submodule is registered. The typical lifecycle is setup/join during bitmap read, bitmap loading across slots, metadata/resync/disk callbacks while the array is active, and leave/stop during teardown.

State and persistence: The header does not own state; all state is behind `mddev->cluster_info` in `md-cluster.c`. Its callback signatures show the persisted/shared concepts: MD event metadata, resync low/high ranges, rdev descriptors, bitmap sizes, and array size changes.

Dependencies/integration: Includes `md.h` and forward-declares MD core types. It is the contract between MD core, bitmap code, and the DLM-backed implementation in `md-cluster.c`.

Risks and test signals: Callback ordering matters. Validate callers handle missing cluster ops, propagate callback errors, and pair start/finish/cancel paths for metadata updates and add-disk operations. Any interface extension must update the concrete `cluster_ops` initializer and all call sites that assume a callback is present.
