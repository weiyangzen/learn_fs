# sources/control-plane/csi-driver-host-path/pkg/hostpath/server.go

## Purpose
This file provides the nonblocking gRPC server wrapper for the hostpath CSI driver and a unary interceptor that logs CSI RPC requests and responses as JSON at high verbosity.

## Important APIs, Types, And Functions
`NewNonBlockingGRPCServer` returns a `nonBlockingGRPCServer`. Methods `Start`, `Stop`, `ForceStop`, and private `serve` manage `grpc.Server` lifecycle. `serve` listens via `endpoint.Listen`, installs `logGRPC`, registers identity, controller, node, group controller, and optional snapshot metadata servers, and serves. `logGRPC` logs requests/responses through `logGRPCJson`, with special handling for `NodePublishVolume` secrets. `logGRPCJson` marshals method, request, response, error string, and full error.

## Control Flow
`Start` launches `serve` in a goroutine and returns immediately. `serve` exits fatally on listen or serve errors. `Stop` gracefully stops the server and runs endpoint cleanup; `ForceStop` stops immediately and also cleans up. Each unary RPC passes through `logGRPC`, then the handler, then JSON logging at verbosity 5.

## State, Persistence, And Dependencies
Server state is the active `grpc.Server` and endpoint cleanup callback. Unix socket files are created and removed by the endpoint package. Dependencies include gRPC, CSI generated registration functions, klog, JSON encoding, context, endpoint, and protosanitizer.

## Integration Points
`hostPath.Run` uses this to expose the driver socket consumed by sidecars, kubelet, socat, and tests. Optional snapshot metadata registration must align with identity capability advertisement.

## Risks
`Stop` assumes `s.server` and `s.cleanup` are initialized; calling it before `serve` has assigned them could panic. `serve` uses `klog.Fatalf`, terminating the process on listen/serve failures. Verbose logging can include sensitive request content except for the special NodePublish secrets sanitization path.

## Test Signals
Tests should start on a temp Unix socket, verify all configured CSI services are registered, call identity RPCs, stop and check socket cleanup, exercise ForceStop, and validate request logging avoids secret leakage.
