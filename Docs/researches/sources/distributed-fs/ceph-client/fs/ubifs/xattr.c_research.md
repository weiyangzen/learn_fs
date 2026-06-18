# sources/distributed-fs/ceph-client/fs/ubifs/xattr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/xattr.c` implements UBIFS extended attributes. UBIFS stores each xattr value as a synchronous internal inode with attached data, and stores each xattr name as an xentry, a directory-entry-like TNC object keyed by the host inode and xattr name. The source was read as a complete 706-line implementation.

## Important APIs, Types, and Functions

Public UBIFS APIs are `ubifs_xattr_set`, `ubifs_xattr_get`, `ubifs_listxattr`, `ubifs_purge_xattrs`, optional `ubifs_init_security`, and `ubifs_xattr_handlers`. Main helpers are `create_xattr`, `change_xattr`, `iget_xattr`, `remove_xattr`, `ubifs_xattr_remove`, `xattr_visible`, `init_xattrs`, and the generic VFS handler callbacks `xattr_get` and `xattr_set`. It uses empty inode/file operation tables for xattr inodes and depends on UBIFS budgeting and journal APIs.

## Control Flow

Set flow validates lock state, value size, and name length, allocates an xentry buffer, takes `host_ui->xattr_sem` for write, looks up the xentry in TNC, then creates, replaces, or rejects based on `XATTR_CREATE` and `XATTR_REPLACE`. Creation budgets a new inode, new xentry, and host inode update, creates an xattr inode, copies value bytes into attached inode data, updates host xattr counters, optionally sets `UBIFS_CRYPT_FL`, and journals the host/xentry/inode update. Replacement loads the existing xattr inode and journals xattr inode plus host inode in an order that keeps fsync semantics. Get flow takes the semaphore for read, resolves xentry to xattr inode, and copies or reports the value length. Remove flow clears link count and journals deletion. List flow walks xentries with `ubifs_tnc_next_ent`, filters hidden/internal names, and emits a NUL-separated list.

## State and Persistence Behavior

Host inode state tracks `xattr_cnt`, `xattr_size`, and `xattr_names`. Xattr value state lives in an internal inode with `ui->xattr = 1`, `UBIFS_XATTR_FL`, synchronous/no-atime/no-ctime flags, `ui->data`, `ui->data_len`, and `i_size`. Xentries and xattr inode updates are persisted through journal operations, and xattr inodes are cached in VFS. Security initialization can create `security.*` attributes during inode creation. `ubifs_purge_xattrs` performs non-atomic cleanup when corrupted media reports too many xattrs.

## Dependencies and Integration Points

The file integrates with `ubifs_new_inode`, TNC lookup/iteration, name/key helpers, journal update/delete/change calls, budgeting, inode flag propagation, fscrypt's encryption context xattr name, Linux VFS xattr handlers, LSM `security_inode_init_security`, capability checks for trusted xattrs, and UBIFS read-only error handling.

## Risks and Edge Cases

Xattr values are limited to `UBIFS_MAX_INO_DATA` and names to `UBIFS_MAX_NLEN`. The list-size limit uses Linux `XATTR_LIST_MAX`, not a native UBIFS media limit. Error paths must roll back host xattr accounting and encryption flags exactly. `ubifs_purge_xattrs` is explicitly non-atomic. Corrupt xentries pointing to non-xattr inodes return errors and may switch the filesystem read-only in purge. The encryption context xattr is internal and hidden from list output. Replacement marks the xattr inode bad on journal failure because old in-memory value bytes have already been overwritten.

## Test Signals

Useful tests include create/replace/remove with all xattr flags, maximum value/name/list sizes, xattr listing visibility for trusted and encryption-context names, security xattr initialization, fsync after xattr change, power-cut replay of create/change/delete, corrupted xentry and excessive xattr count handling, and feature-disabled builds where xattr handlers collapse to `NULL`.
