# sources/distributed-fs/ceph-client/fs/jffs2/acl.h

## Purpose
`acl.h` defines the JFFS2 on-flash ACL structures and conditionally exposes POSIX ACL operation prototypes or no-op macros depending on `CONFIG_JFFS2_FS_POSIX_ACL`.

## Important APIs and types
`struct jffs2_acl_entry` stores tag, permission, and ID for named user/group entries. `struct jffs2_acl_entry_short` stores tag and permission for ACL entries that do not need an ID. `struct jffs2_acl_header` stores the ACL version followed by a flexible entry array. When ACL support is enabled, the header declares `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`.

When ACL support is disabled, `jffs2_get_acl` and `jffs2_set_acl` are defined as `NULL`, and init hooks return zero. This lets the rest of JFFS2 compile without POSIX ACL code while VFS operation tables can omit ACL handlers.

## Control flow and integration
`acl.c` consumes these structures for serialization/deserialization. Other JFFS2 files include this header to wire inode operation ACL hooks and inode creation hooks. The conditional macros mirror the Makefile/Kconfig relationship: `acl.o` is only linked when `CONFIG_JFFS2_FS_POSIX_ACL` is enabled.

## State and persistence behavior
The header defines the layout of persisted ACL xattr payloads. Any change to these structs would be an on-flash format change. The distinction between short and long entries is part of the encoder/decoder contract in `acl.c`.

## Risks and test signals
Risks include ABI drift between the struct layout and `acl.c` size/count calculations, missing ACL operation hooks when the config is enabled, and accidental non-NULL hooks when disabled. Test with ACL enabled and disabled builds, validate serialized ACL byte sizes for short and long entries, and run create/get/set ACL tests against mounted JFFS2 images.
