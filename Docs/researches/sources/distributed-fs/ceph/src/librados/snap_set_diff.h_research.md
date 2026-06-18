# sources/distributed-fs/ceph/src/librados/snap_set_diff.h

## Purpose
This header declares the snapset diff helper used by librados snapshot diff code.

## Important APIs, Types, and Functions
It declares `calc_snap_set_diff()` with inputs for a Ceph context, `librados::snap_set_t`, start and end snap ids, and outputs for changed intervals, end size, end existence, end clone id, and whole-object fallback. The output interval type is `interval_set<uint64_t>`.

## Control Flow
The header has no runtime flow. It defines the linkage contract implemented in `snap_set_diff.cc`.

## State and Persistence Behavior
No state is declared. Callers pass all state explicitly and receive all derived diff state through output pointers.

## Dependencies and Integration Points
It includes common forward declarations, RADOS type definitions, and `interval_set`. It is intended for code that has snapset metadata and needs a reusable extent-diff computation.

## Risks and Test Signals
The interface uses raw output pointers, so callers must provide non-null storage and should initialize no assumptions about prior values. Compile tests should ensure this header can be included wherever only `CephContext` is forward-declared, and unit tests should target the implementation through this declaration.
