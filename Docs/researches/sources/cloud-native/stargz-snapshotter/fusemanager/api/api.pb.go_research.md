# sources/cloud-native/stargz-snapshotter/fusemanager/api/api.pb.go

## Purpose
Generated gogo/protobuf and gRPC bindings for the fuse manager service. It provides Go structs, client interface, server interface, registration, and unary RPC handlers corresponding to `api.proto`.

## Important APIs, Types, And Functions
Defines `StatusRequest`, `InitRequest`, `MountRequest`, `CheckRequest`, `UnmountRequest`, `StatusResponse`, and empty `Response`. `StargzFuseManagerServiceClient` exposes `Status`, `Init`, `Mount`, `Check`, and `Unmount`. `StargzFuseManagerServiceServer`, `UnimplementedStargzFuseManagerServiceServer`, and `RegisterStargzFuseManagerServiceServer` define server-side integration.

## Control Flow
Client methods invoke full method names such as `/fusemanager.StargzFuseManagerService/Mount`. Server handler functions decode requests, call the implementation directly or through a unary interceptor, and return either a response struct or a gRPC error.

## State And Persistence
Generated structs hold request/response fields and proto runtime caches. There is no business persistence; errors are returned through gRPC status, not encoded in `Response`.

## Dependencies And Integration
Depends on `github.com/gogo/protobuf/proto` and `google.golang.org/grpc`. Used by `fusemanager/client.go`, `service.go`, `fusemanager.go`, and tests.

## Risks And Test Signals
Risks are proto/source drift and generated code becoming stale after `api.proto` edits. Compile-time assertions check protobuf and gRPC compatibility. Functional signals come from `fusemanager_test.go`, which exercises the generated client/server path.
