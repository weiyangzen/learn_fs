# sources/distributed-fs/beegfs/common/source/common/nodes/TargetStateStore.h

## Purpose
Declares the target-state store used for reachability and consistency tracking.

## Important APIs, Types, And Functions
Public APIs add/remove targets, sync states alone or with buddy groups, export states as maps/lists, convert states to strings, and inline get/set individual or all states.

## Control Flow
Inline setters update entries by assigning `CombinedTargetState`, which refreshes `TargetStateInfo` timestamps. `getStateUnlocked()` and `getStateInfoUnlocked()` are private helpers behind locked public APIs.

## State, Persistence, And Dependencies
`statesMap` is protected by `RWLock`. `NodeType` is retained for logging/context. Depends on `TargetStateInfo` and mirror buddy group map declarations.

## Integration Points
Attached by `TargetMapper` and node stores; consumed by state sync messages and mirror buddy workflows.

## Risks
Inline `setState()` with an unknown ID will create a new state entry through map indexing. The `setAllStates()` helper changes reachability while preserving consistency.

## Test Signals
Verify unknown-ID behavior for each setter, timestamp updates, list export order, and lock-free helper usage only under locks.
