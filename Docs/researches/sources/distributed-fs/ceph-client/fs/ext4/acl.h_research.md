# sources/distributed-fs/ceph-client/fs/ext4/acl.h

## Purpose

`fs/ext4/acl.h` defines ext4's on-disk POSIX ACL structures, version, size/count helpers, and conditional prototypes or stubs for ACL operations. It is the format contract used by `acl.c` and inode operation tables.

## Important APIs, types, and constants

- `EXT4_ACL_VERSION` is the on-disk ACL format version.
- `ext4_acl_entry` stores tag, permission, and uid/gid id for named user/group entries.
- `ext4_acl_entry_short` stores tag and permission for owner/group/mask/other entries that do not need an id.
- `ext4_acl_header` stores the little-endian version.
- `ext4_acl_size(count)` computes serialized size, using short entries for up to the first four entries and full entries thereafter.
- `ext4_acl_count(size)` validates a serialized size and returns the number of entries or `-1`.
- With `CONFIG_EXT4_FS_POSIX_ACL`, it declares `ext4_get_acl()`, `ext4_set_acl()`, and `ext4_init_acl()`. Without it, get/set pointers become `NULL` and `ext4_init_acl()` is a zero-return stub.

## Control flow

The inline helpers are used before allocating ACL buffers and while parsing xattr values. Conditional compilation lets ext4 code call `ext4_init_acl()` unconditionally during inode creation while operation tables only expose get/set ACL callbacks when support exists.

## State and persistence behavior

The header's structures define persistent ACL xattr bytes. The size/count helpers encode ext4's compact ACL layout, where the common first four ACL entries do not store ids unless the serialized entry type requires it. Disabled ACL builds do not remove on-disk data but do prevent standard ACL operations from interpreting it.

## Dependencies and integration points

The header includes `<linux/posix_acl_xattr.h>` and depends on ext4 transaction handle types through prototypes. It is included by ACL implementation, super/inode operation setup, and new inode creation paths.

## Risks and edge cases

`ext4_acl_count()` mutates an unsigned `size` after subtracting the header, so callers must only pass sizes already checked by parsing code. The "first four short entries" assumption is tied to POSIX ACL canonical ordering; malformed noncanonical ACLs are rejected later by tag validation and core ACL checks. Persistent struct layout cannot change without format impact.

## Test signals

Unit-test `ext4_acl_size()` and `ext4_acl_count()` for zero, one to four, and many entries; malformed byte counts; ACL-disabled builds; and parsing/serializing round trips through `acl.c`.
