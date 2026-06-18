# sources/distributed-fs/openafs/src/afs/HPUX/osi_groups.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_groups.c

Purpose: implements HP-UX PAG embedding in group lists and wraps `setgroups` so existing PAGs survive group-list changes.

Important APIs/types/functions: `Afs_xsetgroups`, `setpag`, static `afs_getgroups`, and static `afs_setgroups`. It uses `PagInCred`, `afs_IsPagId`, `afs_genpag`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, `AddPag`, `crdup`, `crfree`, `set_p_cred`, `cred_lock`, and HP-UX `setgroups`.

Control flow: `Afs_xsetgroups` initializes an AFS request from the current credential, calls the real `setgroups`, and restores the previous PAG if the new groups do not already contain one. `setpag` generates a PAG when requested, reads the current groups, shifts the group list by two slots if no PAG is present, writes the encoded PAG into the first two groups, and calls `afs_setgroups`. `afs_setgroups` either duplicates credentials for current-process replacement or edits the parent credential under credential locks.

State/persistence: PAG state is persisted in the first two group slots of HP-UX credentials. Credential pointers may be replaced on the process or modified in place when `change_parent` is true.

Dependencies/integration: integrates with OpenAFS authentication/PAG logic and HP-UX credential internals. Conditional locking handles HP-UX 11 variants.

Risks/test signals: risks include exceeding `NGROUPS`, races when editing shared credentials, preserving PAG through `setgroups`, and compatibility with parent credential mutation. Test `pagsh`, token visibility after `setgroups`, max group counts, multi-threaded credential changes, and both `change_parent` modes.
