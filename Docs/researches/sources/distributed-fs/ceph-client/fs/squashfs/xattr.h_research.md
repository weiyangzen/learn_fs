# sources/distributed-fs/ceph-client/fs/squashfs/xattr.h

## Purpose

This header abstracts xattr support so the rest of SquashFS can mount images with xattr metadata even when kernel xattr support is disabled.

## Important APIs, Types, and Functions

When `CONFIG_SQUASHFS_XATTR` is enabled it declares `squashfs_read_xattr_id_table()` and `squashfs_xattr_lookup()`. Otherwise it provides inline stubs, defines `squashfs_listxattr` and `squashfs_xattr_handlers` as `NULL`, reads only the xattr id table header to find the preceding table start, logs that xattrs are ignored, and returns `-ENOTSUPP`.

## Control Flow

With xattr support disabled, mount code can still call `squashfs_read_xattr_id_table()`. The stub reads enough metadata to set `xattr_table_start`, returns `-ENOTSUPP`, and lets `super.c` continue when that exact error is seen.

## State and Persistence Behavior

No persistent state is owned. The enabled path uses real xattr table state; the disabled path intentionally leaves xattr handlers absent.

## Dependencies and Integration Points

Included by `super.c`, `inode.c`, `namei.c`, and `symlink.c`. It gates references to xattr implementation files according to Kconfig.

## Risks and Edge Cases

The disabled stub must still preserve table-order parsing during mount; otherwise id/export/fragment table boundaries would be wrong. Returning the wrong error would make xattr-bearing images fail unexpectedly.

## Test Signals

Mount xattr-bearing images with `CONFIG_SQUASHFS_XATTR=n`, verify xattrs are ignored but files mount, and build with xattr enabled/disabled.
