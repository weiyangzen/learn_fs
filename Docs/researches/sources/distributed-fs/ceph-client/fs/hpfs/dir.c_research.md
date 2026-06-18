# sources/distributed-fs/ceph-client/fs/hpfs/dir.c

Purpose: this file implements HPFS directory VFS operations: release, seek, readdir, lookup, and the directory file-operations table.

Important APIs and functions: `hpfs_readdir()` walks dnode trees and emits directory entries. `hpfs_dir_lseek()` validates HPFS synthetic directory positions. `hpfs_lookup()` maps a child name to a dentry/inode. `hpfs_dir_release()` unregisters active readdir positions. `hpfs_dir_ops` exposes directory file operations and shared fsync/ioctl hooks.

Control flow: readdir handles synthetic positions for `.` and `..`, registers the file position for mutation tracking, maps dirents by encoded position, skips first/last sentinel entries, translates names according to mount lowercase settings, and emits entries. Lookup validates the name, searches the dnode tree with `map_dirent()`, creates or reuses an inode by fnode sector, initializes it from either directory/fnode data or directory-entry fast data, rejects unsupported HPFS386 ACL/XPERM entries on writable mounts, and fills timestamps/size/EA metadata from the dirent.

State and persistence: read paths do not persist changes, but `hpfs_add_pos()` and `hpfs_del_pos()` maintain in-memory lists of active directory offsets so dnode mutations can adjust them. Lookup may initialize inode state and cache allocation information.

Dependencies and integration: it depends on dnode traversal/mutation helpers, name validation, inode initialization, EA settings, and HPFS global locking. The file integrates directory reads with `namei.c` mutations that update tracked offsets.

Risks: HPFS directory positions encode dnode sector and entry index; invalid seeks can land in corrupt trees, so strict validation is needed. Cycle detection under `sb_chk` prevents infinite traversal. The lookup fast path for regular files avoids fnode I/O unless EAs require it, so directory-entry metadata must be trustworthy.

Test signals: readdir empty and large directories, lseek to valid/invalid encoded offsets, concurrent create/delete while reading, lowercase mount option, strict-check corrupt dnodes, lookup of files with EAs versus without, unsupported ACL/XPERM entries, and inode timestamp/size initialization from dirents.
