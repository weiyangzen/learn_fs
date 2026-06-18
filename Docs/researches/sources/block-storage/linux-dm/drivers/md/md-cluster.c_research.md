# File Research: sources/block-storage/linux-dm/drivers/md/md-cluster.c

## Purpose
Implements clustered MD coordination using DLM lockspaces and lock value blocks: cluster join/leave, message broadcast, bitmap ownership and recovery, metadata-update serialization, resync range coordination, capacity changes, and clustered disk add/remove/readd operations.

## Main Interfaces
- Cluster lifecycle: `join()`, `leave()`, `slot_number()`, `load_bitmaps()`.
- Metadata protocol: `metadata_update_start()`, `metadata_update_finish()`, `metadata_update_cancel()`.
- Resync protocol: `resync_start()`, `resync_finish()`, `resync_info_update()`, `resync_info_get()`, `area_resyncing()`.
- Disk membership: `add_new_disk()`, `add_new_disk_cancel()`, `new_disk_ack()`, `remove_disk()`, `gather_bitmaps()`.
- Bitmap/capacity helpers: `resize_bitmaps()`, `lock_all_bitmaps()`, `unlock_all_bitmaps()`, `update_size()`.
- Registered operation table: `cluster_ops`.

## Control Flow
Joining allocates `md_cluster_info`, creates a DLM lockspace named from the array UUID and cluster name, waits for slot assignment, creates receive and lock resources (`message`, `token`, `no-new-dev`, `ack`, per-slot `bitmapNNNN`, and `resync`), establishes initial CR/EX locks, and locks the local bitmap slot in PW mode.

Messages are sent by locking the communication token, taking the message lock in EX, copying a `cluster_msg` into its LVB, downconverting message lock state, forcing ACK lock conversion so peer BAST callbacks wake receivers, then restoring ACK and message locks. Receivers read the message LVB under the receive mutex and dispatch by type: metadata updated, resyncing, new disk, remove, re-add, bitmap needs sync, capacity change, or bitmap resize.

Node failure recovery is driven by DLM slot callbacks. Failed slots are recorded in `recovery_map`; a recovery thread locks the failed slot bitmap, copies dirty ranges into the local bitmap, clears suspend ranges, adjusts `recovery_cp`, and wakes MD recovery as needed.

## State And Synchronization
`md_cluster_info` owns DLM resources, receive mutex, suspend spinlock, wait queues, recovery map, local slot number, and state bits such as waiting-for-newdisk, suspend-read-balancing, begin-join, send-lock, send-locked-already, already-in-cluster, pending-recv-event, and holding-md-mutex-for-recvd.

DLM lock resources store lockspace, LVB, name, flags, synchronous wait queue, BAST callback, current mode, and `mddev` backpointer. `recv_mutex` serializes receive processing with token-protected sends. `suspend_lock` protects remote resync suspend ranges.

## Integration Points
Uses Linux DLM (`dlm_new_lockspace()`, `dlm_lock()`, `dlm_unlock()`, lockspace recovery callbacks), MD core locking and recovery, MD bitmap slot helpers, MD metadata reload/update, personality quiesce/resize/size callbacks, kobject uevents for new-device notification, and `register_md_cluster_operations()`.

## Notable Behaviors
- DLM slot numbers are one-based, while clustered MD bitmap slots are zero-based.
- Local bitmap ownership is represented by a persistent PW lock on `bitmapNNNN`.
- Remote resync ranges are stored in the bitmap lock LVB and broadcast with `RESYNCING` messages.
- Peers can mark overlapping read areas as resyncing, temporarily suspending read balancing.
- Adding a disk broadcasts the device UUID and raid slot, then uses `no-new-dev` locking to verify peers can see the device.
- Capacity updates are two-phase: metadata update, peer bitmap sync-size verification, then capacity-change broadcast; failure attempts to revert.
- Leaving with dirty or interrupted recovery broadcasts `BITMAP_NEEDS_SYNC` so another node can continue.

## Risks And Review Focus
- Send/receive locking is delicate: token, ACK, message, receive mutex, and MD reconfig mutex interactions can deadlock if ordering changes.
- Error handling in DLM lock conversion paths must avoid leaving message or ACK locks stuck.
- Cluster bitmap slot copying directly affects recovery correctness after node failure.
- Resize and capacity-change protocols assume peers update bitmap superblocks and report matching sync sizes before capacity is exposed.
- New-disk coordination depends on userspace acknowledging kobject events within a timeout.
