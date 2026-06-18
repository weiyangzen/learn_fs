# sources/cloud-native/containerd/integration/remote/remote_runtime_test.go

## Purpose

`remote_runtime_test.go` verifies that the raw CRI runtime gRPC connection can stream container events over Unix sockets on non-Windows platforms.

## Important APIs, Types, and Functions

- `fakeRuntimeService` embeds the unimplemented CRI runtime server and implements `GetContainerEvents`.
- `TestNewRuntimeClientConnGetContainerEventsUnix` creates a temporary Unix listener, registers a fake gRPC runtime server, dials it with `newRuntimeClientConn`, and receives a created-container event.

## Control Flow

The test starts a gRPC server on a Unix socket, creates a client connection using the adapter helper, opens a `GetContainerEvents` stream, receives the first event, and checks its type.

## State and Persistence Behavior

All state is ephemeral: a Unix socket path under `/tmp`, a listener, a gRPC server, and a client connection cleaned up by `t.Cleanup`.

## Dependencies and Integration Points

It depends on gRPC, CRI runtime API streaming types, Unix sockets, and the `newRuntimeClientConn` behavior in `remote_runtime.go`.

## Risks and Edge Cases

The test specifically protects the passthrough resolver behavior for socket paths. It is skipped on Windows by build tag because Unix sockets are required.

## Test Signals

This is the direct regression signal for CRI event streaming over Unix sockets in the integration remote adapter.
