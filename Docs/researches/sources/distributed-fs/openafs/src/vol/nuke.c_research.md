# sources/distributed-fs/openafs/src/vol/nuke.c

## Purpose
Implements `nuke`, a low-level volume removal routine that deletes all storage associated with a volume id from a partition. It is used when a volume must be forcibly removed outside normal vnode-by-vnode purge paths.

## Important APIs, Types, And Functions
The main exported function is `nuke(char *aname, VolumeId avolid)`. `NukeProc` is the inode-listing callback passed to `ListViceInodes`; it filters `ViceInodeInfo` records for the requested volume or volume group and records inode numbers plus link counts in chunked `struct ilist` lists. The file uses `VGetPartition`, `ListViceInodes`, `IH_INIT`, `IH_DEC`, `namei_HandleToName`, `namei_RemoveDirectories`, `VDestroyVolumeDiskHeader`, and a file-local `localLock`.

## Control Flow
`nuke` validates the partition and volume id, derives the device/partition identity required by `ListViceInodes`, obtains `localLock`, and lists matching inodes through `NukeProc`. For NAMEI, it translates every collected inode to a path and unlinks it directly; for non-NAMEI, it decrements each inode as many times as the recorded link count requires. After data removal, NAMEI tries to prune empty storage directories, and all builds explicitly destroy the volume disk header.

## State And Persistence
Persistent effects are destructive: data files/inodes and the volume header are removed. Runtime state is the temporary linked list of inode batches and the global local lock that prevents concurrent nuke operations in this process. Special inode filtering treats an RW id as matching special files for children in the volume group via parent id.

## Dependencies And Integration Points
`nuke.c` integrates salvage listing (`ListViceInodes`), partition lookup, `ihandle`, volume headers, and NAMEI path conversion. It is a lower-level complement to `purge.c`, which deletes a loaded volume through vnode indexes.

## Risks And Test Signals
Risks are data loss if the wrong volume id or partition is provided, stale or incomplete inode listing, direct NAMEI unlink bypassing link-count adjustment, and partial cleanup if the process exits after data removal but before header destruction. Test signals include nuking test RW and RO volumes, verifying headers disappear, checking NAMEI directory cleanup, and confirming unrelated volumes in the same partition survive.
