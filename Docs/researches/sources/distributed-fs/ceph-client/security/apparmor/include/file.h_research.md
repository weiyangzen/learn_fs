# sources/distributed-fs/ceph-client/security/apparmor/include/file.h

## Purpose
`file.h` defines AppArmor file permission masks, file context state, exec transition index encoding, path conditions, and public APIs for path/open-file mediation.

## Important APIs and types
`struct aa_file_ctx` stores a spinlock, cached label, and allowed mask in the file LSM blob. `struct path_cond` carries object uid and mode for owner/conditional permissions. `AA_X_*` constants encode exec transition type, table index, unsafe, child, inherit, and unconfined flags. Public functions include `aa_audit_file`, `aa_lookup_condperms`, `aa_str_perms`, `aa_path_perm`, `aa_path_link`, `aa_file_perm`, and `aa_inherit_files`.

## Control flow and integration
LSM file hooks map open flags with `aa_map_file_to_perms`, then call path or file revalidation functions. Domain transition code interprets `xindex` flags produced by file permission lookups.

## State and persistence
Per-open-file state lives in the file security blob. Permission masks and xindex values are policy/runtime state, not disk persistence.

## Dependencies
It depends on AppArmor domain, match, permissions, labels, and kernel file structures.

## Risks
The same bit ranges encode file permissions and exec transition metadata, so policy unpacking and domain execution must agree. Cached `aa_file_ctx.allow` can become stale with policy replacement, relying on revalidation paths.

## Test signals
Test `aa_map_file_to_perms` for read/write/append/truncate/create combinations. Exercise exec xindex transitions and file cache revalidation after label changes.
