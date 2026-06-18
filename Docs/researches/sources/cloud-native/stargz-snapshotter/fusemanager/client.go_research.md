# sources/cloud-native/stargz-snapshotter/fusemanager/client.go

## Purpose
Implements a `snapshot.FileSystem` client backed by the fuse manager gRPC service. It lets containerd-stargz-grpc delegate mount, check, and unmount operations to a separate process.

## Important APIs, Types, And Functions
`Client` wraps `pb.StargzFuseManagerServiceClient`. `NewManagerClient` dials the Unix socket and sends `Init`. `newClient` configures grpc transport credentials, containerd Unix dialer, backoff, and message size limits. `Mount`, `Check`, and `Unmount` translate filesystem calls to RPC requests.

## Control Flow
Client creation dials `unix://<socket>`, marshals `Config` as JSON bytes, and calls `Init` with the root path. Later methods allocate the corresponding protobuf request, call the RPC, log on error, and return the gRPC error directly.

## State And Persistence
The client keeps only the generated gRPC client. It does not close the connection explicitly in this file. Durable mount state is owned by the server.

## Dependencies And Integration
Depends on containerd defaults/dialer, grpc insecure transport and backoff, fusemanager protobufs, snapshot `FileSystem`, and the local `Config` type from `service.go`.

## Risks And Test Signals
Risks include connection lifecycle leaks, Init coupling to every client creation, and opaque JSON config compatibility. `fusemanager_test.go` exercises `NewManagerClient` and the Mount/Check/Unmount RPC wrappers against an in-process server.
