# sources/distributed-fs/openafs/src/vol/vutil.c

## Purpose
Implements low-level volume utility operations: volume creation, volume disk-data copying/stat maintenance, `.vol` disk-header read/write/create/destroy, partition volume-header walking, and DAFS-compatible file/disk locking primitives.

## Important APIs And Functions
With `FSSYNC_BUILD_CLIENT`, `VCreateVolume_r` creates the special inode set, initializes the volume info/index/link files, writes the `.vol` disk header, and secretly attaches the new volume. `AssignVolumeName_r`, `CopyVolumeHeader_r`, `ClearVolumeStats_r`, and `CopyVolumeStats_r` manipulate `VolumeDiskData`. `VReadVolumeDiskHeader`, `VWriteVolumeDiskHeader`, `VCreateVolumeDiskHeader`, and `VDestroyVolumeDiskHeader` manage volume header files and DAFS VGC notifications. `VWalkVolumeHeaders` scans partition directories for `.vol` files and retries questionable headers under DAFS partition header locks. `VLockFile*` and `VDiskLock*` implement portable byte-range lock files and intra-process reader/writer coordination.

## Control Flow And State
`VCreateVolume_r` validates partition placement, takes a DAFS volume lock or non-DAFS partition lock, creates each special inode, writes stamps, writes `VolumeDiskData`, creates the disk header, and on failure decrements created inodes and destroys partial headers. Header walking reads without a lock first, retries under lock on DAFS if the read or callback reports a positive error, then calls an error callback for bad headers.

## Persistence And Integration
The file writes persistent volume metadata and special inode files through `IH_CREATE`, `IH_OPEN`, `FDH_PWRITE`, and `.vol` files named by `VFORMAT`. DAFS integrates with `FSYNC_VGCAdd` and `FSYNC_VGCDel` to keep the fileserver volume group cache aligned. Locking abstracts Unix `fcntl`/Windows `LockFileEx` semantics behind volume-package structs.

## Risks And Test Signals
Risks include partial volume creation cleanup gaps, stale VGC entries after disk-header changes, races during header scanning/writing, and lock lifecycle mistakes. Notable behavior: `VLockFileUnlock` closes the lock fd when the refcount drops to zero, relying on close to release the last file lock. Test signals include forced failures after each inode creation step, concurrent create of same id, corrupt `.vol` scan behavior, VGC add/delete error handling, and DAFS multi-thread lock contention.
