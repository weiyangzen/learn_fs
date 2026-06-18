# sources/distributed-fs/ceph-client/fs/jfs/jfs_filsys.h

Purpose: centralizes JFS filesystem option bits, fixed layout constants, block/page conversion macros, reserved disk offsets, reserved inode numbers, and size limits.

Important APIs and constants: mount/superblock flags include `JFS_UNICODE`, `JFS_ERR_*`, quota flags, `JFS_NOINTEGRITY`, `JFS_DISCARD`, commit mode flags, inline log flags, `JFS_BAD_SAIT`, `JFS_SPARSE`, DASD flags, endian/platform flags, and `JFS_DIR_INDEX`. Layout constants include `PSIZE`, `PBSIZE`, `DISIZE`, `IDATASIZE`, `IXATTRSIZE`, `IAG_SIZE`, `INOSPERIAG`, `INOSPEREXT`, `INOSPERPAGE`, block size limits, `MAXFILESIZE`, `JFS_LINK_MAX`, `MINJFS`, fixed block/byte offsets, aggregate reserved inodes, fileset reserved inodes, and `JFS_NAME_MAX`.

Control flow: this header has no executable control flow; it controls branching in other files via mount flag tests and by defining conversion arithmetic used during inode, directory, block-map, and superblock operations.

State and persistence behavior: constants define persistent on-disk geometry. Changing them would alter interpretation of superblocks, inode maps, directory inline areas, inode extents, and reserved metadata locations. Macros like `LBLK2PBLK`, `PBLK2LBLK`, `SIZE2PN`, and `SIZE2BN` translate between logical units used in memory and persisted block/page addressing.

Dependencies and integration: included by JFS directory, inode-map, inode, mount, superblock, dmap, and transaction code. It is tightly coupled to `jfs_dinode.h`, `jfs_imap.h`, `jfs_dtree.h`, and `jfs_xtree.h` layouts.

Risks and edge cases: fixed 4 KiB page assumptions pervade dtree, xtree, imap, and dinode logic. Reserved offset macros assume historical JFS aggregate layout. Flags such as `JFS_DIR_INDEX`, `JFS_OS2`, and `JFS_BAD_SAIT` materially change runtime behavior, so compatibility testing must cover old OS/2/legacy filesystems as well as Linux-created filesystems.

Test signals: mount option parsing, superblock read/write, inode-map addressing, directory indexing enablement, old filesystem compatibility, block-size conversion tests, and fsck/recovery validation of reserved metadata locations.
