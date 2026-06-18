# sources/distributed-fs/openafs/src/vol/listinodes.c

Purpose: platform-specific inode enumeration and conversion support for traditional inode-based OpenAFS partitions. The primary exported behavior is `ListViceInodes`, which scans a partition, identifies AFS vice inodes, optionally filters them through a judge callback, and writes `ViceInodeInfo` records for salvaging and volume utilities. The file is excluded under NAMEI except for conversion-related guarded code.

Important APIs/types/functions: `ListViceInodes` has multiple mutually exclusive implementations: Linux non-NAMEI stub returning unimplemented, AIX/JFS scanner, SGI/XFS scanner, and generic UFS/HPUX/BSD/Sun scanner. Helpers include `ReadSuper`, `IsBigFilesFileSystem`, `ginode`, XFS-specific `xfs_VerifyInode`, `xfs_RenameFiles`, `xfs_ListViceInodes`, generic `bread`, `convertVolumeInfo`, `UpdateThisVolume`, `getDevName`, and client-side `inode_ConvertROtoRWvolume`.

Control flow: scanners sync and briefly sleep to stabilize on-disk state, open raw devices, validate superblocks, iterate inode tables or XFS directory/attribute namespaces, construct `ViceInodeInfo`, run `judgeInode` when supplied, and write records to `inodeFile` if provided. They fsync and size-check output files before returning. XFS additionally validates/chowns attributes, repairs parent inode/tag metadata, queues renames, and can rename files after directory iteration. `inode_ConvertROtoRWvolume` locks/checks out a RO volume, finds special inodes, creates new RW special inodes, copies or converts content, rewrites the volume disk header, removes the old header, and notifies FSSYNC.

State and persistence: global `partition`, `Testing`, and raw-device fd `pfd` support scanner helpers. Persistent effects include optional inode-list file writes, raw device reads, XFS attribute/chown/rename repairs, special inode creation/decrement during RO-to-RW conversion, volume header creation/destruction, and FSSYNC volume state transitions.

Dependencies: old filesystem headers and disk layouts, `osi_inode`, `viceinode.h`, `volinodes.h`, `ihandle.h`, partition/volume APIs, FSSYNC client APIs, XFS attribute syscalls where enabled, and many platform macros.

Integration points: salvager and volume conversion code use `ListViceInodes` to discover vice inodes. `inode_ConvertROtoRWvolume` bridges raw inode scanning, inode-handle I/O, volume headers, and FSSYNC callback/state notifications.

Risks: this file is high-risk because it reads raw filesystem structures and contains many rarely built legacy branches. Several paths use fixed-size buffers and old-style prototypes. XFS repair code mutates namespace/attributes during listing. Generic scanners rely on superblock consistency checks and old disk layout macros. Partial output write/fsync failures return `-2`, distinct from scan failures. There appears to be a suspicious XFS rename loop condition around finding a new name that merits targeted review in that platform branch.

Test signals: platform compile coverage is essential. Behavioral signals include unimplemented Linux path, superblock validation failures, raw-device open/read failures, force-salvage marker detection, judge callback filtering, inode output size/fsync mismatch, XFS attribute version skew, XFS repair/rename dry-run via `Testing`, generic forced-read recovery, and RO-to-RW conversion rollback/error paths.
