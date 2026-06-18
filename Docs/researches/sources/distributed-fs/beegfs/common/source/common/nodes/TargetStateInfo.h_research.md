# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateInfo.h

## Purpose
Defines target reachability and consistency state types, their combined representation, and timestamped internal state records.

## Important APIs, Types, And Functions
`TargetReachabilityState`, `TargetConsistencyState`, `CombinedTargetState`, and `TargetStateInfo` are exported. Serialization maps state enums to `uint8_t`. `TargetStateInfo` extends combined state with `Time lastChangedTime`.

## Control Flow
Assignment from `CombinedTargetState` updates `lastChangedTime`; comparison with combined state ignores timestamp.

## State, Persistence, And Dependencies
State is value-object data. The comment requires enum sync with the client. Depends on `Time` and serialization helpers.

## Integration Points
Used by `TargetStateStore`, `TargetMapper`, storage target info, mirror buddy synchronization, and network messages.

## Risks
Enum order is protocol-visible. Timestamp is relative and not synchronized across nodes, so it is for local freshness only.

## Test Signals
Serialization width, default state offline/good, timestamp update on assignment, and client enum alignment should be checked.
