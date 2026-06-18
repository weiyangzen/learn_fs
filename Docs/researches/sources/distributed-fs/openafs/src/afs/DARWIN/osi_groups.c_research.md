# sources/distributed-fs/openafs/src/afs/DARWIN/osi_groups.c

## Purpose
Implements Darwin PAG placement in process group lists for older kernels and preserves PAGs across `setgroups`. On Darwin 8+ this path is stubbed with `EINVAL`.

## Important APIs, Types, And Functions
`Afs_xsetgroups` wraps native `setgroups` so an existing PAG can be restored. `setpag` inserts or updates the two group slots that encode a PAG. Static helpers `afs_getgroups` and `afs_setgroups` copy and install group arrays into process credentials.

## Control Flow
`Afs_xsetgroups` snapshots the current credential, initializes an AFS request to capture the caller PAG uid, runs native `setgroups`, then if the new credential lacks a PAG and the saved uid is a PAG, calls `AddPag` to restore it. `setpag` generates a PAG if requested, shifts group entries to make room when slots 1 and 2 do not already encode a PAG, writes encoded groups, and installs the credential on the process and optionally its parent.

## State And Persistence
The persistent state is the process credential group list. The file mutates `cr_ngroups`, `cr_groups`, and `proc->p_cred->pc_ucred`, with reference counts around replacement.

## Dependencies And Integration Points
Depends on Darwin credential locking, OpenAFS PAG encoding helpers, native `setgroups`, request initialization, and `AddPag`. It integrates authentication state with Unix group-list semantics.

## Risks
Credential replacement is kernel-version-sensitive and disabled on Darwin 8+ because the older method is not suitable. Group shifting can fail with `E2BIG`. Parent credential changes are potentially surprising and must be explicitly requested. Incorrect refcounting would leak or prematurely free credentials.

## Test Signals
On supported older Darwin builds, test `setpag`, `setgroups` after `klog`, maximum-group handling, parent-changing calls, and PAG preservation after applications modify supplementary groups. Darwin 8+ tests should expect `setpag` failure from this implementation.
