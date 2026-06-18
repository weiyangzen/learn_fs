# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fs.c

Purpose: main bcachefs VFS integration layer. It wires bcachefs inode, directory, file, superblock, export, mount, and lifecycle operations into Linux VFS interfaces.

Key behavior:
- Maintains bcachefs VFS inode cache using `rhashtable` keyed by `subvol_inum` plus a secondary `rhltable` keyed by inode number for open-inode/snapshot checks.
- Synchronizes btree inode state into VFS inodes via `bch2_inode_update_after_write()`.
- Treats VFS atime as the source of truth and folds it into transactional inode updates with `bch2_inode_fold_atime()`.
- Implements create, lookup, link, unlink, symlink, mkdir, rename, tmpfile, getattr, setattr, file attributes, mmap setup, open, readdir, and inode eviction.
- Defines file, directory, symlink, special inode, address-space, export, and superblock operation tables.
- Handles NFS export file handles with bcachefs-specific fid structs containing inode, subvolume, and generation.
- Implements mount flow through `fs_context`: parse options, open/start devices, create or reuse superblock, initialize root inode/dentry, and handle reconfigure read-only/read-write transitions.
- Initializes and tears down VFS resources: inode cache, biosets, writepage buffer pool, writeback workqueue, inode hash tables, and fast inode list.

Important interactions:
- Calls lower bcachefs transactional helpers for inode/dirent/subvolume/quota mutations.
- Delegates buffered and direct I/O operations to `vfs/io.*`, pagecache methods to `vfs/pagecache.*`, xattrs/ACLs to `fs/xattr.*` and `fs/acl.*`, and ioctl handling to `vfs/ioctl.*`.
- Uses per-inode `ei_update_lock` for inode metadata updates and `ei_pagecache_lock` guards for pagecache add/block coordination.
- Contains Linux-version compatibility branches for inode state APIs, mmap setup, fileattr naming, and Unicode dentry behavior.
- Snapshot subvolumes are marked on inodes and excluded from quota accounting.

Notable constraints:
- `bch2_alloc_inode()` is a `BUG()` because inodes are allocated through bcachefs-specific paths.
- Eviction removes or retains hash entries carefully depending on whether the inode is being deleted, so fsck/open-inode checks can see unlinked open inodes.
- Casefold dentry ops are installed selectively to avoid generic casefold overhead on non-casefolded directories.
