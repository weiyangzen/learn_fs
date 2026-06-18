# File Research: sources/cow-pools/openzfs/module/zfs/zfs_znode.c

## Summary
Provides object-to-parent, object-to-path, object-to-stat, and ZPL property lookup helpers for ZFS objsets. Despite the filename, this file is focused on SA-backed lookup utilities and master-node property reads rather than full znode lifecycle management.

## Main Responsibilities
- Initialize SA attribute tables for an objset.
- Safely grab/release SA handles for object numbers.
- Resolve an object's parent and identify xattr directories.
- Build a path string by walking parent object pointers and reverse-searching directory ZAP entries.
- Return lightweight stat data plus path for an object.
- Read selected ZPL properties from objset caches, the master node, or defaults.

## Key APIs
- `zfs_obj_to_pobj()`.
- `zfs_obj_to_path()`.
- `zfs_obj_to_stats()`.
- `zfs_get_zplprop()`.

## Important Behavior
`zfs_obj_to_pobj()` bulk-reads parent, flags, and mode, then verifies that the parent object still exists and is a directory unless the child is an xattr directory. This filters stale parent pointers left behind after unlink operations.

`zfs_obj_to_path_impl()` first checks the delete queue and returns `ESTALE` for unlinked objects. It then walks upward from the object to the root by repeatedly resolving parent object numbers, finding the child's directory entry name with `zap_value_search()`, inserting `/<component>` from the end of the caller buffer backward, and using `<xattrdir>` for xattr directory components.

`zfs_obj_to_stats()` combines `zfs_obj_to_stats_impl()` for mode, generation, link count, and ctime with the path reconstruction helper.

`zfs_get_zplprop()` uses cached objset fields for version, normalization, UTF-8-only, and case sensitivity when initialized. Otherwise it looks up master-node properties, returns defaults for missing values, and caches successful reads back into the objset fields.

## Dependencies
Depends on SA handle APIs, DMU object info, ZAP lookups, master-node names such as `ZFS_SA_ATTRS` and `ZFS_UNLINKED_SET`, ZPL property constants, and zfs_stat output structures.

## Risks
Path reconstruction assumes the caller-provided buffer is large enough; the code asserts rather than returns a clean truncation error if it walks past the buffer start. Parent pointers can be stale after unlink, so callers must handle `ESTALE` and validation errors.
