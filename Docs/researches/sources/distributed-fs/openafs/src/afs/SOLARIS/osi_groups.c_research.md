# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_groups.c

## Purpose
Solaris PAG implementation around `setgroups`, supporting both legacy two-gid PAG encoding and newer one-group PAG encoding.

## Important APIs, Types, and Functions
Exports `afs_xsetgroups`, `setpag`, and, under `AFS_PAG_ONEGROUP_ENV`, `osi_get_group_pag`. Internal helpers include `pag_to_gidset`, `afs_getgroups`, and `afs_setgroups`.

## Control Flow
`afs_xsetgroups` initializes a request from process credentials, calls Solaris `setgroups`, then restores a previously established PAG if the new credentials lack one. `setpag` generates a PAG if needed, allocates a group array sized by `ngroups_max`, locks `curproc->p_crlock`, reads existing groups, encodes the PAG, and calls `afs_setgroups`, which may copy credentials and broadcasts them to all process threads via `crset`.

## State and Persistence
Mutates process credentials and supplemental group lists. No disk state. The encoding location differs: one-gid mode can place a PAG in any group slot; legacy mode writes two gids at the front.

## Dependencies and Integration Points
Depends on Solaris credential APIs (`crgetgroups`, `crsetgroups`, `crcopy`, `crset`), process credential locks, syscall interception in `osi_vfsops.c`, and OpenAFS PAG helpers.

## Risks
Credential lock release is delegated to `afs_setgroups`, so all error paths must be exact. Group-list sizes can be large on Solaris 11, requiring heap allocation instead of small-space allocation. Legacy group ordering can conflict with OS group sorting.

## Test Signals
Setpag on empty/full/large group lists, one-gid and two-gid builds, setgroups PAG preservation, credential propagation to all threads, and error handling when allocation or capacity checks fail.
