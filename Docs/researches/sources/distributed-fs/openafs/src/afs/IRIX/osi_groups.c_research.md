# sources/distributed-fs/openafs/src/afs/IRIX/osi_groups.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_groups.c

Purpose: implements IRIX PAG handling in credentials, including coexistence with SGI DFS PAG conventions and `setgroups` interception.

Important APIs/types/functions: `fixup_pags`, `osi_DFSGetPagFromCred`, `Afs_xsetgroups`, `setpag`, `afs_getgroups`, and `afs_setgroups`. Uses `crdup`, `crfree`, `estgroups`, `OSI_GET_CURRENT_CRED`, `OSI_GET_CURRENT_PROCP`, `PagInCred`, `afs_get_pag_from_groups`, and `afs_get_groups_from_pag`.

Control flow: `Afs_xsetgroups` records old AFS and DFS PAGs, calls native `setgroups`, then uses `fixup_pags` to rebuild credentials if the new group list dropped old PAGs. `fixup_pags` copies user groups, detects new AFS PAG in the first two groups and DFS PAG in the last group, prepends/appends old PAGs if needed, and returns a replacement credential only when changed. `setpag` mirrors other AFS ports by inserting encoded AFS PAG groups at the front. `afs_setgroups` duplicates or edits credentials and installs them with `estgroups`.

State/persistence: AFS PAGs persist in the first two groups; DFS PAGs may persist in the last group. Credential group count `cr_ngroups` is authoritative on IRIX.

Dependencies/integration: integrates with IRIX credential management, SGI DFS compatibility, OpenAFS PAG generation, and syscall replacement in `osi_vfsops.c`.

Risks/test signals: risks include group overflow against `ngroups_max`, preserving both AFS and DFS PAGs, user copyin failures, and credential replacement races. Test AFS and DFS PAG coexistence, `setgroups` with/without PAG slots, max groups, token inheritance, and failed copyin paths.
