# Research: sources/cloud-native/buildkit/executor/executor.go

## Purpose
Core executor package contract.

## Important APIs, Types, and Functions
`Meta`, `MountableRef`, `Mountable`, `Mount`, `WinSize`, `ProcessInfo`, `Executor`, `HostIP`.

## Control Flow
Solver passes mounts and process metadata; implementations materialize specs, run processes, stream IO/signals, and return optional recorders.

## State and Persistence
Contracts only; runtime state lives in implementations.

## Dependencies and Integration Points
Depends on gateway/solver protobufs, cache mounts, and resource recorder types. Boundary between BuildKit solver exec and runtime backends.

## Risks and Edge Cases
Metadata changes affect every backend and can carry security implications.

## Test Signals
Backend compile assertions and integration tests.
