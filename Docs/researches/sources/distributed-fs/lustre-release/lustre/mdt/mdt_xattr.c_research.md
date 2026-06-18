# sources/distributed-fs/lustre-release/lustre/mdt/mdt_xattr.c

## Purpose

`mdt_xattr.c` handles MDT extended-attribute get, list, get-all, set, remove, ACL nodemap translation, and directory-layout finalization through setxattr-style reintegration. It validates client capabilities and xattr namespaces, sizes reply capsules, maps ACL IDs between client and filesystem domains, protects client xattr caches through LDLM locks, and special-cases LMV layout update requests used by directory migration/restripe.

## Important APIs, Types, and Functions

- `mdt_getxattr_pack_reply()` determines reply sizes for single xattr, listxattr, and all-xattrs requests and packs the server capsule.
- `mdt_nodemap_map_acl()` maps POSIX ACL xattr buffers through the export nodemap in either filesystem-to-client or client-to-filesystem direction.
- `mdt_getxattr_all()` returns name list, value blob, and value lengths in the `EADATA`, `EAVALS`, and `EAVALS_LENS` buffers.
- `mdt_getxattr()` is the public get/list/get-all request handler.
- `mdt_dir_layout_update()` finalizes LMV layout changes after migration, split, or merge, including shrink-to-plain-directory through `mo_layout_change(MD_LAYOUT_SHRINK)`.
- `mdt_reint_setxattr()` is the reintegration handler for xattr set/remove and the trusted LMV user-MD shortcut into `mdt_dir_layout_update()`.

## Control Flow

Getxattr first validates SEPolicy, resource IDs, and credentials. Reply packing checks which valid bit is set: `OBD_MD_FLXATTR` fetches the size of a named xattr and handles old-client user-xattr capability and `lustre.pin` name translation; `OBD_MD_FLXATTRLS` sizes the xattr list; `OBD_MD_FLXATTRALL` trusts a caller-provided bounded/aligned size because accurate sizing would be expensive. After packing, `mdt_getxattr()` fetches actual data when the requested `mbo_eadatasize` is nonzero, maps ACLs back to client IDs, shrinks all-xattr buffers to actual lengths, sets reply `OBD_MD_FLXATTR`, and increments stats.

Setxattr validates the namespace before taking locks. User xattrs require `OBD_CONNECT_XATTR`. Trusted xattrs require `CAP_SYS_ADMIN`, except `trusted.lmv` with an LMV user magic is intercepted for layout update. Several internal trusted xattrs are silently ignored or no-op protected, including LOV/LMA/LMV/LINK/FID/VERSION/SOM/HSM/LFSCK namespace and default LMV when disabled. ACLs are mapped from client to filesystem IDs and rejected if mapping changes the length. `lustre.lov.*` names are validated and take layout locks, while `lustre.pin` is translated to the trusted pin xattr after capability/gid checks.

Normal set/remove takes an object lock with update plus perm/xattr/layout bits in `LCK_EX`, sets the VBR target and saves/checks object version, fixes missing ctime from old/bad clients, then calls `mo_xattr_set()` or `mo_xattr_del()`. On success it updates ctime through `mo_attr_set()` with `MDS_PERM_BYPASS`.

Directory layout update resolves the object and its parent, optionally locks the parent update bit if shrink converts to one stripe, locks the directory and stripes, fetches LMV, validates that the layout is changing and that the requested count/hash matches the LMV migration/split/merge state, then either calls `mo_layout_change(MD_LAYOUT_SHRINK)` or clears layout-change flags and migration fields in the LMV xattr while bumping layout version.

## State and Persistence Behavior

Persistent state is xattrs on MDT objects, especially user/trusted namespaces, ACL xattrs, pin xattrs, default LMV, and LMV layout xattrs. The file also persists ctime updates after xattr changes. Request/reply state lives in capsule fields `RMF_EADATA`, `RMF_EAVALS`, `RMF_EAVALS_LENS`, `RMF_ACL`, and `RMF_MDT_BODY`. Layout update mutates LMV flags/version and can physically shrink directory layout through the lower layout-change method.

## Dependencies and Integration Points

The file depends on Linux xattr and Lustre ACL/nodemap APIs, ptlrpc capsules, `mdt_object_find_lock()`, VBR helpers from `mdt_reint.c`, LMV helpers, layout-change methods, RBAC/capability checks, client connection flags, and lprocfs counters. It integrates with the restriper, because `mdt_restripe_layout_update()` synthesizes a `REINT_SETXATTR` record that lands in `mdt_dir_layout_update()`.

## Risks and Edge Cases

- `OBD_MD_FLXATTRALL` relies on a bounded client size estimate; too small a buffer leads to lower get failures and shrunken zero output.
- Protected trusted xattrs often return success without changing state. That compatibility behavior can hide caller mistakes.
- ACL mapping can fail due to nodemap lookup, size limits, old-client ACL limits, or non-length-preserving ID mapping.
- Layout update compares little-endian LMV fields and user values; future changes must preserve endian handling.
- Shrink-to-one-stripe changes parent namespace/FID behavior and therefore takes extra parent locking; missing this lock would corrupt namespace consistency.
- `mdt_getxattr_pack_reply()` treats missing `trusted.lov` as zero-length success for old client compatibility, unlike most missing xattrs.

## Test Signals

Tests should cover single/list/all getxattr sizing, missing `trusted.lov`, old-client user-xattr rejection, `lustre.pin` translation, ACL map success/failure/size limits, all-xattr buffer shrink behavior, trusted protected no-op xattrs, set/remove ctime update, VBR replay mismatch, layout update for migration/split/merge, shrink to one stripe, hash/count mismatch errors, layout already complete `-EALREADY`, and cache invalidation/lock cancellation through xattr/perms/layout inode bits.
