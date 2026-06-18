<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/super.c -->
## sources/distributed-fs/ceph-client/fs/romfs/super.c

Purpose: implements the ROMFS VFS driver for block and MTD-backed read-only ROM filesystem images. It wires the filesystem type, mount context, superblock parsing, inode allocation, directory lookup, directory iteration, and file data reads around the ROMFS on-media structures declared in `internal.h`.

Important APIs and types: `romfs_fs_type`, `romfs_context_ops`, `romfs_super_ops`, `romfs_dir_operations`, `romfs_dir_inode_operations`, `romfs_aops`, and the slab-backed `romfs_inode_info` cache are the main integration points. `romfs_iget()` is the central inode constructor; `romfs_read_folio()` is the page-cache read path; `romfs_readdir()` and `romfs_lookup()` walk directory file-header chains; `romfs_fill_super()` validates the image and installs the root dentry.

Control flow: module init creates `romfs_inode_cachep` and registers `romfs`. Mounting calls `romfs_init_fs_context()`, `romfs_get_tree()`, then either `get_tree_mtd()` or `get_tree_bdev()`. `romfs_fill_super()` sets read-only superblock properties, reads the first 512 bytes, validates magic, image size, and checksum, derives the root inode offset from the volume name length, calls `romfs_iget()`, and builds `s_root`. Lookup and readdir repeatedly use `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()` to follow `next` pointers and resolve hard-link file headers.

State and persistence: all persistent state is on the ROMFS image. Runtime state is limited to `s_fs_info` holding the image size, inode private offsets (`i_metasize`, `i_dataoffset`), page-cache folios, and the inode slab. The filesystem is forced `SB_RDONLY | SB_NOATIME`; reconfigure synchronizes and reasserts read-only.

Dependencies and integration: depends on VFS mount/context APIs, page cache, block and MTD helpers, dcache lookup, generic read-only file ops, special inode setup, endian conversion, and ROMFS device access helpers. `romfs_kill_sb()` must release MTD or block-device references matching the selected mount path.

Risks: malformed images can create long or looping directory chains; the code bounds traversal by `romfs_maxsize()` but checksum verification only covers the initial header. `romfs_iget()` notes that per-file checksum validation is not done. Directory names use a fixed `ROMFS_MAXFN` stack buffer. Error mapping in `romfs_readdir()` returns `0` after read errors, matching legacy directory iteration behavior but reducing observability.

Test signals: mount valid and invalid ROMFS images on both block and MTD configurations, verify checksum rejection, root offset derivation, hard-link resolution, symlink readback, special inode device numbers, executable bit propagation, short reads in `romfs_read_folio()`, `statfs` fields, and read-only remount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/super.c -->
