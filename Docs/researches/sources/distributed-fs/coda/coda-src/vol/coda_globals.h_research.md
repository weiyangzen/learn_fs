# sources/distributed-fs/coda/coda-src/vol/coda_globals.h

## Purpose

`sources/distributed-fs/coda/coda-src/vol/coda_globals.h` declares global constants and the top-level recoverable segment layout for the Coda file server's volume storage.

## Important APIs, Types, and Functions

It defines `MAXVOLS`, `LARGEFREESIZE`, `SMALLFREESIZE`, `LARGEGROWSIZE`, `SMALLGROWSIZE`, `bool_t`, `struct camlib_recoverable_segment`, external `camlibRecoverableSegment`, and the `SRV_RVM(name)` accessor macro.

## Control Flow

There is no runtime flow. Code accesses fields in the recoverable segment through `SRV_RVM`.

## State and Persistence Behavior

`camlib_recoverable_segment` is recoverable global state: initialization flag, fixed `VolumeList[MAXVOLS]`, small/large vnode free lists and indices, maximum allocated volume id, reserved space, and dummy padding. This structure anchors all volume headers and vnode free-list state in RVM.

## Dependencies and Integration Points

It depends on `VolHead`, `VnodeDiskObject`, and `VolumeId` from volume headers. Recovery, volume allocation, and vnode allocation code use `camlibRecoverableSegment` and `SRV_RVM` to address persistent server state.

## Risks and Edge Cases

`MAXVOLS` is fixed at 1024 and must remain a power of two. The recoverable segment layout is persistent; field changes require migration. Free-list sizes scale from `MAXVOLS`, so changing capacity affects memory/RVM layout. The macro trusts `camlibRecoverableSegment` is initialized and correctly mapped.

## Test Signals

Run fresh RVM initialization, restart recovery, volume allocation up to capacity boundaries, free-list depletion/growth tests, and layout/migration checks for any change to the segment structure.
