## sources/distributed-fs/openafs/src/afs/NBSD/osi_groups.c

Purpose: NetBSD PAG group manipulation and `setgroups` syscall interception support.

Important APIs and state: defines `Afs_xsetgroups`, `setpag`, and static helpers `osi_getgroups` and `osi_setgroups`. It uses NetBSD `kauth_cred` group APIs and constants `NOUID`, `NOGID`, and `NGROUPS`. PAG values are encoded into group slots through `afs_get_groups_from_pag` and decoded with `afs_get_pag_from_groups`.

Control flow: `Afs_xsetgroups` initializes an AFS request from the process credentials, calls the real `sys_setgroups`, and if the resulting credentials no longer contain a PAG but the original request UID was a PAG id, it calls `AddPag` to restore it. `setpag` generates a PAG if requested, reads current groups, makes room for two PAG groups at positions 1 and 2 if none are present, encodes the new PAG, and calls `osi_setgroups`. `osi_setgroups` enters NetBSD credential modification, optionally duplicates credentials when not changing the parent, calls `kauth_cred_setgroups`, and leaves credential modification.

Dependencies and integration: depends on NetBSD syscall args, kauth credentials, OpenAFS PAG helpers, and the syscall hook installed by `osi_kmod.c` or legacy LKM code in `osi_vfsops.c`. It integrates process authentication state with OpenAFS PAG semantics.

State and persistence: modifies process credential group lists in memory. PAGs persist with credentials across process lifetime/fork semantics, not on disk.

Risks: group-list manipulation is sensitive to `NGROUPS` limits and exact PAG group slot placement. Incorrect `change_parent` semantics can modify the wrong credential object. `Afs_xsetgroups` must preserve PAGs without overwriting explicit PAGs supplied by the caller.

Test signals: `setpag` with and without existing PAG, near-`NGROUPS` group lists returning `E2BIG`, ordinary `setgroups` preserving PAG, child/parent credential behavior, and kauth group visibility through NetBSD APIs.
