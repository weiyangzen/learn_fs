# sources/distributed-fs/beegfs/common/source/common/nodes/NodeOpStats.h

## Purpose
Defines the common base for per-client and per-user operation statistics and the wire-vector layout for exporting counters.

## Important APIs, Types, And Functions
Constants define per-IP and metadata vector positions, reserved header size, layout version, and safety length. `NodeOpCounterMap` maps `uint128_t` IP/user keys to `OpCounter`. `NodeOpStats` exposes `mapToUInt128Vec()` and `removeClientFromMap()`.

## Control Flow
The header establishes that vectors begin with metadata, then repeated key plus counters. Derived classes are expected to update `clientCounterMap` and `userCounterMap` under `lock`.

## State, Persistence, And Dependencies
State is in-memory and protected by `RWLock`. It depends on `OpCounter`, `Node`, and common vector typedefs.

## Integration Points
Used by metadata and storage node operation-stat subclasses and management tooling.

## Risks
Adding operation counters changes the number of elements per key and must be compatible with consumers. Removing only client keys does not affect user counters.

## Test Signals
Static checks should confirm reserved position math and that derived counter counts match exported names.
