# sources/cloud-native/containerd/api/services/leases/v1/leases_grpc.pb.go

## Purpose

This generated file binds the Leases service to gRPC when `!no_grpc` is active. It defines client/server interfaces, registration, handlers, and the `Leases_ServiceDesc`.

## Important APIs, Types, and Functions

`LeasesClient` exposes `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`. `NewLeasesClient` wraps a `grpc.ClientConnInterface`, and each method invokes a full method path. `LeasesServer` requires the six methods plus `mustEmbedUnimplementedLeasesServer`. `UnimplementedLeasesServer` returns `codes.Unimplemented`. `RegisterLeasesServer` registers the service descriptor.

Handler functions decode each request type, optionally pass through a unary interceptor, and dispatch to the typed service implementation.

## Control Flow

Client calls are unary `cc.Invoke` calls with allocated response structs. Server handlers create a concrete request, call the decoder, and either call the service directly or wrap the call in interceptor metadata with the full method name.

## State and Persistence Behavior

This file has no persistent state. Lease storage and resource retention live behind the registered service implementation. The generated descriptor is immutable registration metadata.

## Dependencies and Integration Points

Dependencies are `context`, gRPC packages, and `emptypb`. It integrates with daemon gRPC registration, middleware/interceptors, clients, and message definitions in `leases.pb.go`.

## Risks and Test Signals

Risks include forward-compatibility embedding requirements, method-name drift, interceptor side effects, and build exclusion under `no_grpc`. Tests should smoke-test all six RPCs over gRPC, verify unimplemented behavior, exercise interceptors, and compile after proto regeneration.
