# sources/cloud-native/cri-o/internal/lib/container_server_test_inject.go

## Purpose
Provides test-only setters for injecting mocked storage services into `ContainerServer`.

## Important APIs, Types, And Functions
- `SetStorageRuntimeServer(server storage.RuntimeServer)`.
- `SetStorageImageServer(server storage.ImageServer)`.

## Control Flow
Build-tagged with `//go:build test`. Each setter directly replaces the corresponding unexported field.

## State And Persistence
Mutates in-memory `ContainerServer` fields. No persistence.

## Dependencies And Integration Points
Used by tests that need to replace storage runtime/image service dependencies with mocks without exposing setters in production builds.

## Risks And Edge Cases
Only available with the `test` build tag. Tests can create inconsistent server state by injecting nil or incompatible mocks.

## Test Signals
Supports checkpoint/container server tests; no standalone assertions.
