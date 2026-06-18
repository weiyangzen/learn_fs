# sources/distributed-fs/openafs/src/afs/FBSD/osi_groups.c

## Purpose
Provides FreeBSD PAG preservation around `setgroups` and a partial `setpag` implementation for encoding PAGs in supplementary groups.

## Important APIs, Types, And Functions
`Afs_xsetgroups` wraps `sys_setgroups`. `setpag` generates/inserts a PAG group pair. Static `afs_getgroups` copies group arrays, while `afs_setgroups` is currently a stub returning zero.

## Control Flow
`Afs_xsetgroups` duplicates the thread credential, initializes an AFS request to capture existing PAG identity, invokes native `sys_setgroups`, then if the new credential lacks a PAG and the saved uid encodes one, calls `AddPag`. `setpag` allocates a group buffer sized by `ngroups_max + 1`, shifts existing groups to create slots 1 and 2 if needed, writes encoded PAG groups, and calls the stubbed `afs_setgroups`.

## State And Persistence
Intended persistent state is the thread credential group list, but this file's `afs_setgroups` stub does not install the modified groups. Temporary group arrays are allocated with `osi_Alloc`.

## Dependencies And Integration Points
Depends on FreeBSD thread/sysproto `setgroups`, OpenAFS PAG helpers, credential duplication, and `AddPag`.

## Risks
The `setpag` path appears incomplete because `afs_setgroups` returns success without mutating credentials. This can make PAG creation appear successful while not changing process groups, depending on how `AddPag` is implemented for FreeBSD. Group buffer sizing and slot assumptions also require care.

## Test Signals
Explicitly test `setpag` result by checking `PagInCred` after the call, not just return code. Also test `setgroups` after PAG creation, maximum group counts, and failure cleanup of allocated group buffers.
