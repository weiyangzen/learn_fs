# sources/distributed-fs/openafs/src/afs/OBSD/osi_groups.c

## Purpose
OpenBSD PAG preservation and creation logic around `setgroups`, implemented by storing PAG identifiers in supplemental groups.

## Important APIs, Types, and Functions
Exports `Afs_xsetgroups` and `setpag`. Internal helpers are `afs_getgroups` and `afs_setgroups`. Uses `afs_genpag`, `afs_IsPagId`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, `PagInCred`, and `AddPag`.

## Control Flow
`Afs_xsetgroups` initializes a request under GLOCK, calls the real `setgroups`, then restores the caller's previous PAG if the new credentials do not already contain one. `setpag` generates a PAG if requested, copies the current group list, ensures there is space for two PAG gids at positions 1 and 2, writes the encoded PAG gids, and installs the modified groups via `afs_setgroups`.

## State and Persistence
State is stored in process credentials, either by copying credentials when `change_parent` is false or modifying the supplied credential pointer. No disk persistence exists.

## Dependencies and Integration Points
Depends on OpenBSD `struct ucred`, `struct proc`, `crcopy`, syscall argument layout, and OpenAFS PAG helpers. Hooked from OpenBSD VFS init by replacing `SYS_setgroups`.

## Risks
Group-list capacity is limited by `NGROUPS`; adding a PAG can fail with `E2BIG`. The two-gid PAG encoding assumes specific group ordering. Credential copying and `p_rcred` aliases are kernel-version sensitive.

## Test Signals
Verify `setpag` for empty and full group lists, preservation of existing PAGs across `setgroups`, successful credential copy when not changing parent, and behavior when `ngroups + 2 > NGROUPS`.
