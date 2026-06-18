# sources/cloud-native/containerd/api/services/sandbox/v1/sandbox_grpc.pb.go

## Purpose

This generated file exposes the sandbox `Store` and `Controller` services over gRPC when the `no_grpc` build tag is not set. It is the typed client/server binding for the semantic contract in `sandbox.proto`.

## Important APIs, Types, and Functions

`StoreClient` and `NewStoreClient` provide unary `Create`, `Update`, `Delete`, `List`, and `Get` methods using `ClientConnInterface.Invoke`. `StoreServer`, `UnimplementedStoreServer`, `UnsafeStoreServer`, `RegisterStoreServer`, handler functions, and `Store_ServiceDesc` define server registration and interceptor paths. The controller side mirrors that pattern with `ControllerClient`, `ControllerServer`, `UnimplementedControllerServer`, `RegisterControllerServer`, nine unary handlers, and `Controller_ServiceDesc`.

## Control Flow

Client calls allocate a response struct, invoke `/containerd.services.sandbox.v1.<Service>/<Method>`, and return either the populated response or the transport error. Server handlers decode one request, call the implementation directly or through a unary interceptor, and type-assert the request before dispatch. Both service descriptors have empty stream lists.

## State and Persistence Behavior

The binding is stateless except for holding the client connection. Persistence and runtime state are delegated to the registered service implementation. Unimplemented stubs return gRPC `Unimplemented` status errors.

## Dependencies and Integration Points

It depends on `google.golang.org/grpc`, `codes`, `status`, and the message types from `sandbox.pb.go`. The compile-time assertion requires gRPC-Go v1.32.0 or later. Containerd daemons and clients use the service names `containerd.services.sandbox.v1.Store` and `containerd.services.sandbox.v1.Controller`.

## Risks

The file is generated and should not be hand-edited. Server implementations must embed the unimplemented server for forward compatibility unless they deliberately opt out with the unsafe interface. Interceptor behavior is part of the request path, so auth/namespace middleware depends on exact full method strings.

## Test Signals

Signals include gRPC registration smoke tests, interceptor coverage for every unary method, unimplemented-method behavior, generated-code compile checks under `!no_grpc`, and cross-checks that gRPC method names match the proto.
