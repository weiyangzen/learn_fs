# Research: sources/cloud-native/buildkit/executor/oci/mounts_test.go

## Purpose
Tests for OCI mount helpers.

## Important APIs, Types, and Functions
Tests prefix matching, removal, and dedup ordering.

## Control Flow
Builds sample mounts, applies helpers, compares results.

## State and Persistence
No state.

## Dependencies and Integration Points
Depends on Go testing and runtime-spec mounts. Protects spec mount construction.

## Risks and Edge Cases
Does not exercise real kernel mounts.

## Test Signals
`go test ./executor/oci` signal.
