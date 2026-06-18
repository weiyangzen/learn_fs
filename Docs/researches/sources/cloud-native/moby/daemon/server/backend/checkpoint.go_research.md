# sources/cloud-native/moby/daemon/server/backend/checkpoint.go

## Purpose
Defines backend option structs for checkpoint list and delete operations.

## Important APIs, Types, And Functions
`CheckpointListOptions` carries `CheckpointDir`. `CheckpointDeleteOptions` carries `CheckpointID` and `CheckpointDir`.

## Control Flow
Type definitions only.

## State And Persistence
No state is changed. These options guide daemon checkpoint filesystem operations elsewhere.

## Dependencies And Integration Points
Used by checkpoint router handlers and daemon checkpoint backend methods.

## Risks And Edge Cases
Correct directory and checkpoint ID validation is left to backend implementations.

## Test Signals
Router checkpoint tests or daemon checkpoint tests validate use of these structs.
