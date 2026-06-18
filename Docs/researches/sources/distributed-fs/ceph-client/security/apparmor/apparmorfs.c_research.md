# sources/distributed-fs/ceph-client/security/apparmor/apparmorfs.c

## Purpose
`apparmorfs.c` implements AppArmor's user-visible filesystem interfaces: securityfs entries under `/sys/kernel/security/apparmor`, a private single-superblock apparmorfs policy tree, policy load/replace/remove files, policy query transactions, profile/namespace introspection, namespace revision polling, and optional raw binary policy export.

## Important APIs and functions
- Filesystem setup and teardown: `aa_create_aafs`, `aa_destroy_aafs`, `apparmorfs_fill_super`, `aafs_create`, `aafs_remove`, and `aa_mk_null_file`.
- Policy writes: `profile_load`, `profile_replace`, `profile_remove`, and shared `policy_update`.
- Namespace/profile tree maintenance: `__aafs_ns_mkdir`, `__aafs_ns_rmdir`, `__aafs_profile_mkdir`, `__aafs_profile_rmdir`, and `__aafs_profile_migrate_dents`.
- Revision signaling: `__aa_bump_ns_revision`, `ns_revision_read`, `ns_revision_poll`.
- Query support: `aa_write_access`, `query_label`, `query_data`, and the `multi_transaction` buffer helpers.
- Raw export, under `CONFIG_SECURITY_APPARMOR_EXPORT_BINARY`: `__aa_fs_create_rawdata`, `__aa_fs_remove_rawdata`, `rawdata_open`, and zstd decompression helpers.

## Control flow
At initialization, `aa_create_aafs` mounts private apparmorfs, creates static securityfs feature files, root `.load/.replace/.remove/revision` files, builds the root policy tree under `.policy`, and exposes a magic `policy` symlink that redirects readers to the current task's policy namespace. Policy write handlers first check `aa_may_manage_policy`, copy complete user writes from offset zero into `aa_loaddata`, and call `aa_replace_profiles` or `aa_remove_profiles`.

The dynamic policy tree mirrors namespaces and profiles with dentries whose inode-private data stores refcounted namespaces, proxies, or raw load data. Namespace directories contain profiles, raw_data, revision, policy-management files, and subnamespace directories. Profile directories expose name, mode, attach string, optional hash, and optional raw data symlinks.

## State and persistence
The visible filesystem is generated kernel state, not persistent storage. It pins dentries and references through `aa_common_ref` and apparmorfs mount counts. Namespace revisions are long counters with wait queues; raw policy data is retained in `aa_loaddata` when export is enabled and linked into `ns->rawdata_list`. The `.null` character device path is stored in global `aa_null` and used when unauthorized inherited files are replaced.

## Dependencies and integration
The file integrates with securityfs, VFS simple filesystem helpers, zstd, policy unpack/load code, policy namespaces, labels/proxies, audit permission checks, resource/cap/net feature tables, and the current task label/namespace helpers. Userspace tools rely on its feature directories and transaction formats for policy discovery and queries.

## Risks
This code has a large VFS and lifetime surface. Inode-private references must match dentry removal and inode eviction exactly. Namespace lock ordering is delicate, especially where inode locks are dropped before namespace operations. Raw policy export can consume memory and requires correct decompression bounds. Query parsing accepts binary strings with embedded NULs, so off-by-one mistakes would be security relevant. Feature reporting is a userspace ABI and changes can break parsers.

## Test signals
Boot with AppArmor enabled and verify securityfs entries, feature files, `.load/.replace/.remove`, `revision`, `profiles`, and `policy` symlink behavior. Load, replace, and remove policies across namespaces and confirm revision polling wakes. Test `.access` label/profile/labelall/data transactions including malformed NUL layouts and oversized writes. With raw export enabled, verify raw_data metadata, hash, compressed size, raw decompression, and profile symlinks.
