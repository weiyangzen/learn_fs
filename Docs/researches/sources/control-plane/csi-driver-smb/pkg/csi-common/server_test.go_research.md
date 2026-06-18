# sources/control-plane/csi-driver-smb/pkg/csi-common/server_test.go

## Purpose
Smoke tests for the non-blocking gRPC server wrapper.

## Important APIs, Types, and Functions
Tests `NewNonBlockingGRPCServer`, `Start`, direct `serve`, `Wait`, `Stop`, and `ForceStop`.

## Control Flow
Uses ephemeral TCP endpoints and sleeps to avoid races, then relies on test mode to stop serving.

## State and Persistence
Creates transient local listeners and in-memory gRPC servers.

## Dependencies
Uses grpc, sync, time, and testify/assert.

## Integration Points
Guards the server wrapper used by driver startup.

## Risks and Edge Cases
Sleep-based timing can be flaky. It does not exercise Unix socket cleanup, registered service calls, or nil-server stop behavior.

## Test Signals
Passing tests indicate basic lifecycle methods do not panic in expected paths.
