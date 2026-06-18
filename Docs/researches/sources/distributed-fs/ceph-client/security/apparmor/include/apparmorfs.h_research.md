# sources/distributed-fs/ceph-client/security/apparmor/include/apparmorfs.h

## Purpose
This header defines apparmorfs/securityfs entry descriptors, namespace/profile dentry index enums, access macros, and exported functions for creating/removing AppArmor filesystem state.

## Important APIs and types
`struct aa_sfs_entry` describes static securityfs files and directories with boolean/string/u64/FOPS values. Macros such as `AA_SFS_FILE_BOOLEAN`, `AA_SFS_FILE_STRING`, `AA_SFS_FILE_U64`, `AA_SFS_FILE_FOPS`, and `AA_SFS_DIR` build entry arrays. The `AAFS_NS_*` and `AAFS_PROF_*` enums index `dents[]` arrays in namespaces and profiles. Functions include `aa_create_aafs`, `aa_destroy_aafs`, `__aa_bump_ns_revision`, profile/ns mkdir/rmdir/migration helpers, and rawdata creation/removal stubs or implementations.

## Control flow and integration
Policy namespace/profile code calls these helpers when policy objects are created, replaced, or removed. Static feature arrays in `apparmorfs.c` use the entry macros to build securityfs. Rawdata functions compile to no-ops unless export binary support is enabled.

## State and persistence
The header standardizes dentry slots used as in-memory references from `aa_ns` and `aa_profile`. `aa_null` is a global path used to replace unauthorized inherited descriptors.

## Dependencies
It depends on VFS dentry/file operations, AppArmor profile and namespace structures, and optional raw policy load data.

## Risks
Dentry index order is a contract with profile/ns allocation and removal code; mismatches can remove or expose the wrong file. Rawdata stubs must preserve caller semantics when export is disabled.

## Test signals
Compile with export binary on/off. Load/replace/remove profiles and namespaces while verifying all dentry slots are created, migrated, and removed without leaks or stale files.
