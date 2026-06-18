# sources/control-plane/csi-lib-utils/rpc/common_test.go

## Purpose

This test file validates the RPC helper behavior in `common.go` using real gRPC servers bound to Unix sockets and fake CSI service implementations.

## Important APIs and Flow

`tmpDir` creates temporary socket directories. `startServer` creates a `grpc.Server`, conditionally registers fake Identity, Controller, and GroupController services, serves on a Unix socket in a goroutine, and returns a cleanup function that stops the server and removes the socket. Table tests cover `GetDriverName`, plugin capabilities, controller capabilities, group-controller capabilities, and `ProbeForever`. Fake service structs embed unimplemented CSI servers and return configured responses or errors. `fakeIdentityServer.Probe` consumes a planned sequence and counts calls.

## State, Dependencies, and Integration

Each test owns temp filesystem state, a Unix socket, a gRPC server goroutine, and a client connection created through the package's `connection.Connect` helper with a metrics manager. Dependencies include Go testing, gRPC, CSI generated types, wrapperspb, testify `require`, klog test contexts, and csi-lib-utils connection/metrics packages.

## Risks and Test Signals

The tests exercise real network/socket plumbing, which is stronger than pure mocks but can be sensitive to cleanup timing. They verify nil capability skipping and retry counts, but do not test context cancellation in `ProbeForever`. Passing `go test ./rpc` is the primary signal.
