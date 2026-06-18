# sources/distributed-fs/ceph-client/fs/ntfs3/super.c

## Purpose
`super.c` owns NTFS3 filesystem registration, fs_context parsing, mount/remount, superblock initialization, procfs metadata, sync/unmount, export operations, boot parsing, discard, and module lifecycle.

## Important APIs and Functions
It provides rate-limited logging, shared `$UpCase` table management, mount option parsing, remount validation, procfs `volinfo` and `label`, super operations, export operations, `ntfs_init_from_boot()`, `ntfs_fill_super()`, `ntfs_unmap_meta()`, `ntfs_discard()`, `ntfs_init_fs_context()`, `ntfs3_kill_sb()`, and module init/exit.

## Control Flow
Mount allocates context state, loads NLS, parses primary or alternate boot geometry, initializes block sizes and limits, then loads `$Volume`, `$MFTMirr`, `$LogFile` and replays it, enforces dirty-volume policy, loads `$MFT`, `$Bitmap`, `$BadClus`, `$AttrDef`, `$UpCase`, `$Secure`, `$Extend/$Reparse`, `$Extend/$ObjId`, and finally the root inode. Sync writes metadata inodes, clears dirty state when possible, updates MFT mirror, and flushes the block device.

## State and Persistence Behavior
`ntfs_sb_info` receives geometry, serial, version, dirty flags, label, bitmap state, MFT mirror counts, attribute definitions, EA/reparse limits, and shared upcase. RW mounts can clear dirty state, update primary boot from a valid alternate boot, write labels, update `$MFTMirr`, and issue discard.

## Dependencies and Integration Points
The file integrates with VFS, block devices, fs_context, exportfs, procfs, NLS, slab caches, and NTFS3 log, bitmap, security, object id, reparse, inode, index, and label modules.

## Risks
Mount is the trust boundary. Geometry validation, boot fallback, journal replay policy, dirty gating, shared upcase reference counts, teardown ordering, and MFT bitmap extent merging are sensitive. RW mount after failed replay is blocked.

## Test Signals
Test clean/dirty volumes, replay success/failure, alternate boot fallback, sector mismatches, huge clusters, invalid record/index sizes, truncated images, bad clusters, remounts, procfs label writes, statfs, NFS exports, discard alignment, and multi-mount upcase sharing.
