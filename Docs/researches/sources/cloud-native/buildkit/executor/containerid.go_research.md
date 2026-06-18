# Research: sources/cloud-native/buildkit/executor/containerid.go

## Purpose
Validation helper for executor container IDs.

## Important APIs, Types, and Functions
`ValidContainerID` enforces safe runtime/filesystem ID syntax.

## Control Flow
Executors call it before registering or creating runtime state.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on simple string validation. Used by runc and containerd executors.

## Risks and Edge Cases
Rules must be safe for runtime names and paths without rejecting valid clients unnecessarily.

## Test Signals
`containerid_test.go` covers accepted/rejected IDs.
