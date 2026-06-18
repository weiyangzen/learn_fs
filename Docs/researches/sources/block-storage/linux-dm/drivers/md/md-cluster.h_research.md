# File Research: sources/block-storage/linux-dm/drivers/md/md-cluster.h

## Purpose
Declares the clustered MD operation table used by MD core to call optional cluster support.

## Main Interfaces
`struct md_cluster_operations` contains callbacks for:
- Cluster lifecycle: `join`, `leave`, `slot_number`.
- Resync tracking: `resync_info_update`, `resync_info_get`, `resync_start`, `resync_finish`, `area_resyncing`.
- Metadata serialization: `metadata_update_start`, `metadata_update_finish`, `metadata_update_cancel`.
- Disk membership: `add_new_disk`, `add_new_disk_cancel`, `new_disk_ack`, `remove_disk`.
- Bitmap coordination: `load_bitmaps`, `gather_bitmaps`, `resize_bitmaps`, `lock_all_bitmaps`, `unlock_all_bitmaps`.
- Capacity changes: `update_size`.

## Control Flow
This file only declares the callback contract. Runtime behavior is supplied by `md-cluster.c` when the module registers its `cluster_ops`.

## State And Synchronization
No state is defined here. The callback contract implies callers must be prepared for cluster-wide locking, DLM-backed synchronization, and MD reconfig/recovery interactions.

## Integration Points
Included by MD core and clustered MD implementation to bridge generic MD code with optional cluster-specific behavior.

## Notable Behaviors
- The API explicitly separates metadata update start/finish/cancel so callers can hold cluster communication locks across MD superblock updates.
- Bitmap and capacity operations are part of the same cluster contract as disk membership, reflecting that recovery state is distributed.

## Risks And Review Focus
- Callback callers must know whether the MD reconfig mutex or other MD locks are held for each operation.
- Adding callbacks requires updates to both clustered and non-clustered call sites or stubs.
