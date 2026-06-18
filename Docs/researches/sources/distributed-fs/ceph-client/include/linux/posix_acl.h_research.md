# sources/distributed-fs/ceph-client/include/linux/posix_acl.h

Purpose: declares in-kernel POSIX ACL representation, reference management, VFS ACL operations, inode ACL cache helpers, and filesystem helper callbacks.

Important APIs and types: `struct posix_acl_entry` stores tag, permission bits, and UID/GID union. `struct posix_acl` stores refcount, entry count, RCU head, and counted flexible entries. Helpers include `FOREACH_ACL_ENTRY`, `posix_acl_dup()`, `posix_acl_release()`, allocation/init/clone/from-mode/equiv-mode/create/chmod/update helpers, `get_posix_acl()`, `set_posix_acl()`, cached ACL get/set/forget helpers, validation, permission checking, `simple_set_acl`, `simple_acl_create`, VFS get/set/remove/listxattr APIs, and `get_inode_acl()`.

Control flow: filesystem and VFS code allocate or fetch ACLs, refcount them when sharing, validate entries against user namespaces, use create/chmod helpers to adjust inode modes and default/access ACLs, cache ACLs in inode fields, and release references through RCU-safe freeing. VFS xattr operations route POSIX ACL names to filesystem `get_acl`/`set_acl` equivalents.

State and persistence: ACL objects are reference-counted in-memory structures; persistent ACL data lives in filesystem xattrs or on-disk metadata. Inode ACL caches hold runtime references and must be invalidated on changes.

Dependencies and integration points: integrates with VFS inodes/dentries, mount idmaps, user namespaces, xattrs, RCU, refcounts, slab allocation, and UAPI POSIX ACL tags. With `CONFIG_FS_POSIX_ACL` disabled, ACL creation returns no ACLs and VFS ACL operations return `-EOPNOTSUPP` or no-op.

Risks and test signals: risks include refcount leaks, use-after-free without `posix_acl_dup()`, stale inode ACL cache after xattr updates, mode/ACL equivalence mistakes, idmapped mount translation errors, invalid entry ordering, and disabled-config assumptions. Test ACL create/chmod, permission checks, xattr get/set/remove/list, cache invalidation, idmapped mounts, RCU cached lookups, and no-POSIX-ACL builds.
