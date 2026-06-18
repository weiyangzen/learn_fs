# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_acl.c

## Scope

FreeBSD ZFS NFSv4 ACL implementation. It handles old and FUID ACL formats, ACL storage in SA or external DMU objects, mode derivation, chmod/chown ACL updates, ACL inheritance, get/set ACL operations, and access checks for regular access, delete, and rename.

## Main Interfaces

- Format ops: `zfs_acl_v0_ops` and `zfs_acl_fuid_ops`.
- Allocation/lifetime: `zfs_acl_alloc()`, `zfs_acl_node_alloc()`, `zfs_acl_free()`.
- Version/storage: `zfs_external_acl()`, `zfs_znode_acl_version()`, `zfs_acl_node_read()`, `zfs_aclset_common()`.
- Conversion: `zfs_acl_xform()`, `zfs_vsec_2_aclp()`, `zfs_copy_ace_2_fuid()`, `zfs_copy_fuid_2_ace()`, `zfs_copy_ace_2_oldace()`.
- Mode and chmod/chown: `zfs_mode_compute()`, `zfs_acl_chown_setattr()`, `zfs_acl_chmod_setattr()`.
- Creation/inheritance: `zfs_acl_ids_create()`, `zfs_acl_ids_free()`, `zfs_acl_ids_overquota()`.
- User APIs: `zfs_getacl()` and `zfs_setacl()`.
- Access checks: `zfs_has_access()`, `zfs_zaccess()`, `zfs_zaccess_rwx()`, `zfs_zaccess_unix()`, `zfs_zaccess_delete()`, `zfs_zaccess_rename()`, and `zfs_fastaccesschk_execute()`.

## State And Control Flow

The ACL is represented as `zfs_acl_t` containing a list of `zfs_acl_node_t` buffers and format-specific operation callbacks. Old ACLs store fixed `zfs_oldace_t`; FUID ACLs support compact owner/group/everyone ACE headers, explicit FUID ACEs, and object ACEs.

Reading computes ACL size/count from SA or legacy znode ACL fields, allocates a node, loads embedded, external, or SA ACE data, caches read-only ACLs on the znode, and maps checksum errors to `EIO`. Setting updates mode/pflags/ctime and writes ACL data either into SA attributes, embedded legacy znode fields, or an external DMU ACL object, allocating/freeing external objects as size/version changes.

Mode computation walks ACEs in order and derives POSIX mode bits from the first relevant owner/group/everyone read/write/execute decisions. Chmod rebuilds ACLs around trivial mode ACE masks while optionally preserving inheritable special ACEs and trimming groupmask permissions. Creation can inherit parent ACEs according to dataset `aclinherit`/`aclmode`, synthesize trivial ACLs, create FUID owner/group ids, and handle setgid policy.

Access checking first rejects dataset/flag conflicts such as read-only mounts, immutable data writes, quarantined reads/execs, and nounlink delete. It then evaluates ACEs in NFSv4 order, removes decided bits from the working mask, tracks deny masks, supports append fallback, and finally consults FreeBSD privilege policy for unresolved bits.

## Dependencies

Uses ZPL znodes/vnodes, SA attributes, DMU transactions/objects, ZIL ACL logging, FUID/idmap mapping, quota checks, FreeBSD credential and secpolicy helpers, NFSv4 ACL common routines, dataset ACL properties, and vnode locks.

## Correctness Notes

`z_acl_lock` and vnode lock expectations are strict on read/set paths. ACL cache replacement occurs during set and after successful writes. Delete/rename follow NFSv4 delete-child/delete semantics plus BSD-specific directory write requirements. FreeBSD intentionally ignores individual alternate data stream permissions for many xattr operations to avoid bogus `EACCES`.
