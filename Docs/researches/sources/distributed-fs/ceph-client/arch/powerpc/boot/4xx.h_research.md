# sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.h

## Purpose
Public boot-wrapper declarations for the 4xx helper routines implemented in `4xx.c`.

## Important APIs, Types, And Control Flow
The header declares memory fixups, reset/quiesce helpers, EBC range fixup, and 440GP/EP/GX/SPE clock fixups. There is no runtime logic in the header; it is the integration contract for board-specific wrappers.

## State, Dependencies, Risks, And Tests
State is managed by `4xx.c` through hardware registers and FDT updates. Dependencies are `u32` types from boot-wrapper headers and object inclusion under `CONFIG_44x`. Risks are stale declarations causing build failures or board wrappers calling helpers not linked for a given config. Test by compiling all 4xx wrapper targets and checking each declared helper resolves.
