
# sources/distributed-fs/openafs/src/uss/uss_acl.c

Purpose: `uss_acl.c` implements ACL and quota operations for `uss`. It converts between AFS external ACL text and internal linked lists, applies positive or negative ACL changes, sets volume quotas, and restores final ACLs for directories staged during account creation.

Important APIs and functions: exported `uss_acl_SetAccess()` parses an argument containing a path followed by user/right pairs, fetches the current ACL with `uss_fs_GetACL()`, optionally clears it, applies each pair, externalizes the result, and writes it with `uss_fs_SetACL()`. `uss_acl_SetDiskQuota()` builds a `uss_VolumeStatus_t` payload and calls `uss_fs_SetVolStat()`. `uss_acl_CleanUp()` walks `uss_currentDir` and restores each saved final ACL. Internal helpers include `Convert()` for rights names or `rlidwka` characters, `ParseAcl()`, `AclToString()`, `ChangeList()`, `FindList()`, `PruneList()`, and `foldcmp()`.

Control flow: ACL modification first isolates the path, then repeatedly consumes `user rights` fields separated by spaces. For clear operations it starts from `EmptyAcl()`; otherwise it parses the current cache-manager ACL buffer. Rights set to zero are pruned from the chosen list. Cleanup restores directories in reverse creation order because `uss_currentDir` is a stack.

State and persistence: internal ACL structures are heap-allocated; cleanup frees the `uss_subdir` chain but not all temporary ACL nodes allocated during `uss_acl_SetAccess()`. Persistent state is AFS ACL and quota metadata via cache-manager pioctls.

Dependencies and integration: depends on AFS rights constants from `prs_fs.h`, cache-manager wrappers in `uss_fs.c`, common parsing in `uss_common_FieldCp()`, global verbosity/dry-run/account-creator state, and `uss_VolumeStatus_t` from `uss_common.h`.

Risks: `AclToString()` concatenates into a static `AFS_PIOCTL_MAXSIZE` buffer without explicit bounds checks. `ChangeList()` uses `strcpy()` into a 100-byte name field after callers accept up to 64-byte user fields, so current call sites are bounded but the helper is fragile. Allocation failures are not consistently checked. `uss_acl_CleanUp()` ignores return codes from final ACL restoration. Test signals should exercise clear versus merge behavior, negative ACLs, rights aliases, zero-right pruning, oversized ACLs, invalid rights characters, quota payload length, and cleanup after multi-directory template creation.
