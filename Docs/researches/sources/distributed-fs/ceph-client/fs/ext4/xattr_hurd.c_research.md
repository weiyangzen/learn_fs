# sources/distributed-fs/ceph-client/fs/ext4/xattr_hurd.c

## Purpose

`fs/ext4/xattr_hurd.c` implements the ext4 VFS xattr handler for GNU Hurd-prefixed attributes. It is a thin namespace adapter that maps the VFS `XATTR_HURD_PREFIX` namespace to ext4's on-disk `EXT4_XATTR_INDEX_HURD` namespace.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_hurd_list()`, `ext4_xattr_hurd_get()`, `ext4_xattr_hurd_set()`, and exports `ext4_xattr_hurd_handler`. The handler's `.prefix` is `XATTR_HURD_PREFIX`; `.list`, `.get`, and `.set` point to the local wrapper functions.

## Control Flow

Listing and access are gated by the ext4 mount option `XATTR_USER`. `ext4_xattr_hurd_list()` returns true only when that option is set on the dentry superblock. `ext4_xattr_hurd_get()` and `ext4_xattr_hurd_set()` return `-EOPNOTSUPP` if `XATTR_USER` is not enabled; otherwise they call `ext4_xattr_get()` or `ext4_xattr_set()` with `EXT4_XATTR_INDEX_HURD`.

## State and Persistence Behavior

This file does not manage storage itself. It persists values through the common ext4 xattr engine, which may store the attribute in the inode body, external EA block, or EA inode depending on size and feature flags. The only persistent discriminator introduced here is the `EXT4_XATTR_INDEX_HURD` name index on each xattr entry.

## Dependencies and Integration Points

It depends on ext4 mount-option helpers from `ext4.h`, the common xattr API from `xattr.h`, and VFS xattr handler dispatch. The handler is included in `ext4_xattr_handler_map` and `ext4_xattr_handlers` from `xattr.c`, which makes it visible to ext4 inode operations and xattr listing.

## Risks and Edge Cases

The main behavioral risk is policy coupling to `XATTR_USER`: disabling user xattrs also disables Hurd xattrs. The get/set wrappers ignore the `mnt_idmap` argument, which is expected for raw xattr storage but should remain consistent with VFS handler signatures. All corruption, journaling, quota, and size risks are delegated to `xattr.c`.

## Test Signals

Mount ext4 with and without `user_xattr` and verify Hurd-prefixed xattrs list, get, set, replace, and remove only when the option permits them. Also verify that entries persist with the Hurd name index and that errors from the common ext4 xattr engine propagate unchanged.
