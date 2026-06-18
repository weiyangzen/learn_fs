# sources/distributed-fs/ceph-client/fs/ntfs/volume.h

## Purpose
Defines the legacy NTFS driver's in-memory volume/superblock state and inline helpers for volume flags, free-space counters, MFT counters, bitmap-page counters, and dirty-cluster reservations.

## Important APIs, Types, And Functions
`struct ntfs_volume` stores VFS linkage, mount options, NTFS geometry, system-file inodes, volume flags/version/label, NLS and upcase state, allocator cursor state, free-space accounting, and background work. `DEFINE_NVOL_BIT_OPS()` emits `NVolFoo()`, `NVolSetFoo()`, and `NVolClearFoo()` helpers for flags such as `Errors`, `CaseSensitive`, `FreeClusterKnown`, `Shutdown`, `Discard`, and `DisableSparse`. Inline helpers update cluster/MFT counters and `lcn_empty_bits_per_page`, waiting for the initial free-cluster scan when required.

## Control Flow
`super.c` allocates and initializes this structure in `ntfs_init_fs_context()`, populates geometry from the boot sector, stores system inodes during mount, and frees it at unmount. Allocation and statfs paths consume the atomic counters and wait queue to avoid using unknown free-space state.

## State And Persistence
The structure mirrors persistent NTFS state but is itself in-memory. Persistent fields cached here include `$Volume` flags, serial number, version, volume label, `$AttrDef`, `$UpCase`, MFT and bitmap locations, and system-file inode references. Atomic free counters and dirty reservations model current runtime allocation state.

## Dependencies And Integration Points
Included broadly by legacy NTFS code. It depends on Linux synchronization, wait queues, uid/gid, workqueues, errseq, and NTFS on-disk layout definitions. `super.c`, allocation code, inode code, directory code, and statfs all consume these fields.

## Risks And Edge Cases
Several helpers block until `NVolFreeClusterKnown`, so they must not run before `free_waitq` is initialized and the background scanner can wake waiters. MFT free-record helpers gate on `FreeClusterKnown`, not a separate MFT-known flag, making initialization coupling important. Dirty-cluster release clamps underflow to zero, which avoids negative accounting but can hide mismatched reservations.

## Test Signals
Verify mount initialization defaults, flag toggles through mount options, free-space wait/wakeup behavior, statfs after dirty reservations, MFT record counter updates, shutdown flag behavior, and teardown of all system inode pointers.
