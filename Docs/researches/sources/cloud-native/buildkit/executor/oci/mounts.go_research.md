# Research: sources/cloud-native/buildkit/executor/oci/mounts.go

## Purpose
OCI mount manipulation helpers.

## Important APIs, Types, and Functions
`withRemovedMount`, `hasPrefix`, `dedupMounts`.

## Control Flow
Transform runtime-spec mount lists during spec generation.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on containerd OCI spec options and runtime-spec mounts. Used by `GenerateSpec` and platform helpers.

## Risks and Edge Cases
Path-prefix correctness is security-sensitive.

## Test Signals
`mounts_test.go` covers pure behavior.
