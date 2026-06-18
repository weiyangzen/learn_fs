# sources/cloud-native/moby/daemon/server/router/checkpoint/backend.go

## Purpose
Defines the checkpoint router backend interface.

## Important APIs, Types, And Functions
`Backend` requires `CheckpointCreate`, `CheckpointDelete`, and `CheckpointList`, using API checkpoint request/summary types and backend checkpoint option structs.

## Control Flow
Interface definition only.

## State And Persistence
No state is changed by this file. Implementations perform checkpoint filesystem/runtime operations.

## Dependencies And Integration Points
Implemented by the daemon checkpoint backend and consumed by checkpoint router handlers.

## Risks And Edge Cases
The router depends on backend methods returning correctly classified errors for HTTP mapping.

## Test Signals
Compile-time conformance and checkpoint route tests validate this contract.
