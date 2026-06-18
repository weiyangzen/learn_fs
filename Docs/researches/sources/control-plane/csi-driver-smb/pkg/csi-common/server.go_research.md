# sources/control-plane/csi-driver-smb/pkg/csi-common/server.go

## Purpose
Non-blocking gRPC server wrapper for CSI identity, controller, and node services.

## Important APIs, Types, and Functions
Defines `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, and `nonBlockingGRPCServer` methods `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`.

## Control Flow
`Start` launches `serve` in a goroutine. `serve` parses endpoint, removes existing Unix socket, listens, creates a gRPC server with `logGRPC` interceptor, registers supplied CSI services, and serves until stopped. Test mode schedules a graceful stop.

## State and Persistence
Holds a waitgroup and gRPC server pointer. Removes/recreates Unix socket files for Unix endpoints.

## Dependencies
Depends on net, os, runtime, sync, grpc, CSI protobuf registration, klog, and `ParseEndpoint`.

## Integration Points
Used by SMB driver `Run` to expose CSI services.

## Risks and Edge Cases
`Stop` and `ForceStop` assume `s.server` is initialized. Fatal logging exits the process on endpoint/listen errors. Test-mode waitgroup choreography is unusual and timing-sensitive.

## Test Signals
`server_test.go` smoke-tests construction, start, serve, wait, stop, and force stop.
