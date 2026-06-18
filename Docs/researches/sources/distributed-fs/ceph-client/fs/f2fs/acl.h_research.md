# sources/distributed-fs/ceph-client/fs/f2fs/acl.h

## Purpose

`fs/f2fs/acl.h` defines the F2FS on-disk POSIX ACL xattr format and exposes ACL entry points or stubs depending on `CONFIG_F2FS_FS_POSIX_ACL`.

## Important APIs, Types, and Functions

The persistent format version is `F2FS_ACL_VERSION`. `struct f2fs_acl_header` stores the little-endian version. `struct f2fs_acl_entry_short` stores tag and permissions for ACL entries that do not need an ID. `struct f2fs_acl_entry` extends that with a little-endian UID/GID ID for named user and group entries.

When POSIX ACL support is enabled, the header declares `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. When disabled, `f2fs_get_acl` and `f2fs_set_acl` are NULL macros and `f2fs_init_acl()` is an inline no-op returning zero.

## Control Flow

The header's conditional declarations let common F2FS inode and creation code call ACL hooks without linking `acl.o` when ACL support is disabled. With ACL enabled, calls are dispatched to `acl.c`; without ACL, creation proceeds without ACL initialization.

## State and Persistence Behavior

The structs define the byte layout stored as F2FS POSIX ACL xattr values. All numeric fields are little-endian. The short-entry optimization means the serialized size depends on tag order and count; parsing code in `acl.c` must agree exactly with these definitions.

## Dependencies and Integration Points

The header includes `<linux/posix_acl_xattr.h>` for POSIX ACL constants and types. It is consumed by F2FS inode creation, xattr, and ACL implementation code. Kconfig and the F2FS Makefile determine whether the real implementation is linked.

## Risks and Edge Cases

Any ABI change to these structs would affect existing on-disk ACL xattrs. The disabled-config stubs must remain consistent with callers' expectations; for example, creation must not fail just because ACL support is compiled out.

## Test Signals

Build tests should cover ACL enabled and disabled. Format tests should verify serialized sizes, version checks, little-endian conversion, and compatibility between `acl.h` layout and `acl.c` parser/serializer.
