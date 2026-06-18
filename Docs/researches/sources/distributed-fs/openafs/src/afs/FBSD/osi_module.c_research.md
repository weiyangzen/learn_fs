# sources/distributed-fs/openafs/src/afs/FBSD/osi_module.c

## Purpose
Registers the FreeBSD AFS filesystem module and defines the OpenAFS malloc type.

## Important APIs, Types, And Functions
`MALLOC_DEFINE(M_AFS, "afsmisc", ...)` defines the allocation bucket. `VFS_SET(afs_vfsops, afs, VFCF_NETWORK)` registers the VFS module using the `afs_vfsops` table.

## Control Flow
There is no explicit load/unload function here; FreeBSD module registration is declarative through `VFS_SET`.

## State And Persistence
Persistent kernel module state is managed by the FreeBSD VFS module framework and the `M_AFS` allocator statistics.

## Dependencies And Integration Points
Depends on `afs_vfsops` from `osi_vfsops.c`, FreeBSD module/VFS macros, and allocation users in `osi_misc.c`.

## Risks
Registration correctness depends on `afs_vfsops` and module metadata matching FreeBSD expectations. The module is marked `VFCF_NETWORK`, affecting mount semantics.

## Test Signals
Kernel module load should expose the `afs` VFS type, allocation statistics should use `afsmisc`, and mount should dispatch into `afs_vfsops`.
