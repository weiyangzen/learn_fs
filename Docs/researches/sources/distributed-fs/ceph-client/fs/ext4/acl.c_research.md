# sources/distributed-fs/ceph-client/fs/ext4/acl.c

## Purpose

`fs/ext4/acl.c` implements POSIX ACL support for ext4 using xattrs as the persistent storage format. It converts between ext4's on-disk ACL encoding and Linux `struct posix_acl`, retrieves ACLs through ext4 xattr get, sets ACLs transactionally through ext4 xattr set, updates inode mode for access ACL changes, and initializes inherited ACLs for new inodes.

## Important APIs, types, and functions

- `ext4_acl_from_disk()` validates ACL header version, counts entries, allocates a `posix_acl`, converts little-endian tags/perms/ids, and rejects malformed sizes or tags.
- `ext4_acl_to_disk()` serializes a `posix_acl` into ext4 ACL header plus short/full entries.
- `ext4_get_acl()` implements inode `get_posix_acl`, rejects RCU mode with `-ECHILD`, maps access/default types to xattr indexes, fetches the xattr, and converts it.
- `__ext4_set_acl()` maps ACL type to xattr name index, rejects default ACLs on non-directories, serializes the ACL, calls `ext4_xattr_set_handle()`, and updates the inode ACL cache.
- `ext4_set_acl()` performs quota initialization, computes xattr journal credits, starts an `EXT4_HT_XATTR` transaction, optionally calls `posix_acl_update_mode()`, sets the ACL xattr, marks inode dirty if mode changed, stops the journal, and retries ENOSPC through `ext4_should_retry_alloc()`.
- `ext4_init_acl()` uses `posix_acl_create()` to inherit/default ACLs during new inode creation and stores them with `XATTR_CREATE`.

## Control flow

ACL reads perform a size query, allocate an exact buffer, read the xattr value, then parse it. ACL writes run inside a journal transaction. For access ACLs, VFS permission semantics can require inode mode changes; the code computes the new mode before setting the xattr and marks the inode dirty in the same transaction. New inode initialization is called while inode creation already owns an ext4 journal handle, so `__ext4_set_acl()` is used directly without starting a nested transaction.

## State and persistence behavior

Persistent ACLs are xattrs under `EXT4_XATTR_INDEX_POSIX_ACL_ACCESS` and `EXT4_XATTR_INDEX_POSIX_ACL_DEFAULT` with `EXT4_ACL_VERSION`. In-memory ACLs are cached in `inode->i_acl` and `inode->i_default_acl` via `set_cached_acl()` or explicit NULL assignment during initialization. Access ACL writes may persist both an xattr and an inode mode change atomically through JBD2.

## Dependencies and integration points

The file depends on POSIX ACL core helpers, ext4 xattr credit calculation and set/get APIs, JBD2 transaction handles, quota initialization, ext4 inode dirtying, idmapped mount mode update support through `mnt_idmap`, and allocation retry logic from `balloc.c`.

## Risks and edge cases

Malformed ACL xattrs must be rejected without reading beyond the buffer. UID/GID conversion uses `init_user_ns`, so id translation assumptions are explicit. Default ACLs on non-directories return `-EACCES` unless clearing. Journal credit calculation must cover serialized ACL size, and ENOSPC retry must not repeat non-ENOSPC errors. If xattr setting succeeds but mode dirtying fails, callers see an error after partial metadata changes in a journal context.

## Test signals

Test get/set/remove access and default ACLs, default ACL rejection on regular files, ACL inheritance during create, mode updates from access ACL changes, malformed ACL xattr sizes/tags/version, quota initialization failures, ENOSPC retry, idmapped chmod/ACL interactions, remount with ACL support disabled, and crash recovery around ACL plus mode updates.
