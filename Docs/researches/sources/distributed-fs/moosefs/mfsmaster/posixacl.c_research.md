# sources/distributed-fs/moosefs/mfsmaster/posixacl.c

## Purpose
`posixacl.c` is the MooseFS master-side in-memory POSIX ACL table. It stores access and default ACL records by `(inode, acltype)`, computes effective access modes for clients, copies inherited default ACLs during file creation, serializes ACL metadata, and reloads ACLs during metadata import.

## Important APIs, Types, And Functions
The file defines private `acl_entry` records with `id` and `perm`, and `acl_node` records with inode, ACL type, base user/group/other permissions, mask, named-user count, named-group count, dynamic ACL entry table, and hash-chain link. Hashing is generated through `hash_begin.h`/`hash_end.h` with `LOHASH_BITS 20` and the `posix_acl_xxx` prefix.

Important exported functions are `posix_acl_getmode()`, `posix_acl_setmode()`, `posix_acl_accmode()`, `posix_acl_copydefaults()`, `posix_acl_set()`, `posix_acl_remove()`, `posix_acl_get_blobsize()`, `posix_acl_get_data()`, `posix_acl_getall()`, `posix_acl_check()`, `posix_acl_copy()`, `posix_acl_store()`, `posix_acl_load()`, `posix_acl_cleanup()`, and `posix_acl_init()`.

`posix_acl_create()` is the internal allocator. It initializes an empty node and inserts it into the generated hash table.

## Control Flow
ACL lookups use the generated hash table. `posix_acl_getmode()` derives the mode bits from access ACL user permission, mask, and other permission. `posix_acl_setmode()` updates those low permission bits when chmod changes a file mode.

Permission evaluation flows through `posix_acl_accmode()`. UID 0 receives full access. The owner uses `userperm`. Named users are masked by `mask`. Group membership checks both the owning GID and named groups and ORs matching access modes. If no group entry matches, the function falls back to `otherperm`.

Inheritance is handled by `posix_acl_copydefaults()`. If the parent default ACL is simple, it only adjusts the new inode mode. Otherwise it creates or updates the child access ACL, clamps permissions by the parent default ACL, copies named entries, and, for directories, also copies the parent's default ACL onto the child.

Mutation flows through `posix_acl_set()` and `posix_acl_remove()`. A simple access ACL with no named entries and `mask == 0xFFFF` is represented by no explicit ACL node, and the filesystem ACL flag is cleared. Non-simple ACLs are inserted or resized and set `fs_set_aclflag()`.

## State, Persistence, And Dependencies
The module owns all ACL nodes in memory. Each node owns an optional `acltab` array sized to `namedusers + namedgroups`. `posix_acl_cleanup()` frees every table and node and destroys the generated hash state.

Persistent storage is a stream of fixed headers plus optional 6-byte named entries. Each record stores inode, ACL type, four permission fields, and two counts, followed by `(id, perm)` pairs. An all-zero header terminates the stream. `posix_acl_load()` skips ACLs for missing inodes, validates ACL type, optionally ignores duplicate/bad records, sets filesystem ACL flags, and contains a compatibility repair for metadata version `0x10` entries with zero masks.

Dependencies include `MFSCommunication.h` for `POSIX_ACL_ACCESS`, `POSIX_ACL_DEFAULT`, and mode mapping, `datapack.h` for binary packing, `filesystem.h` for inode/mode/ACL-flag integration, `bio.h` via the header for metadata I/O, and MooseFS logging/assertion helpers.

## Integration Points
`filesystem.c` uses these APIs for FACL get/set, chmod mode synchronization, ACL inheritance when creating inodes, ACL copy on snapshot/link-like operations, and metadata load/store. The restore path parses `SETACL` changelog records into `fs_mr_setacl()`, which then reaches this module through filesystem code.

## Risks
`posix_acl_getmode()` assumes an access ACL node exists; callers must only call it when the inode ACL flag is present or after a lookup has been validated.

The header declares `posix_acl_set()` as returning `int`, but this C file implements it as `void`. Existing callers ignore the return value, but the mismatch is a compile-time/interface risk.

`posix_acl_copy()` assumes the source ACL exists and dereferences `sacn` without a null check. Callers must prove the source ACL flag/record exists.

ACL entry order is not canonicalized by `posix_acl_set()`. `posix_acl_check()` compares named users within the user range and named groups within the group range, but duplicates could make equality checks ambiguous.

## Test Signals
Useful tests include mode extraction and chmod synchronization, root/owner/named-user/group/other access resolution, named group OR behavior, default ACL inheritance for files and directories, simple ACL elision, duplicate and invalid metadata load handling with and without ignore mode, version `0x10` zero-mask repair, ACL copy/remove cleanup, and round-trip store/load with multiple named users and groups.
