# sources/cloud-native/containerd/api/services/sandbox/v1/sandbox_ttrpc.pb.go

## Purpose

This generated file exposes the sandbox Store and Controller services over containerd's ttrpc transport. It provides lighter-weight RPC bindings commonly used on local sockets and in runtime-adjacent components.

## Important APIs, Types, and Functions

`TTRPCStoreService` declares the five store methods. `RegisterTTRPCStoreService` registers service name `containerd.services.sandbox.v1.Store` with a method map whose handlers unmarshal into concrete request values and call the implementation. `NewTTRPCStoreClient` returns a client implementing the same interface and each method uses `client.Call`. `TTRPCControllerService`, `RegisterTTRPCControllerService`, `NewTTRPCControllerClient`, and the controller client methods follow the same unary pattern for the nine runtime operations.

## Control Flow

Server registration builds ttrpc method closures. Each closure unmarshals the request, propagates unmarshal errors, and dispatches to the service. Client methods allocate a concrete response, call the exact service/method pair, and return the response pointer on success.

## State and Persistence Behavior

The file holds no persistent state. The ttrpc client stores only a `*ttrpc.Client`; the registered server delegates state to the service implementation. Request and response state is serialized through the generated protobuf messages.

## Dependencies and Integration Points

It depends on `github.com/containerd/ttrpc` and the sibling protobuf types. It integrates with runtimes or shims that register sandbox APIs over ttrpc rather than gRPC.

## Risks

Unlike the gRPC server binding, there are no generated unimplemented forward-compatibility stubs; implementers must satisfy the full interface at compile time. Service and method string drift would break wire compatibility. Context cancellation and deadlines rely on ttrpc propagation and implementation behavior.

## Test Signals

Useful tests register fake ttrpc services, invoke every Store and Controller method, verify unmarshal failures surface, confirm service names/method names, and compare behavior with gRPC bindings for equivalent payloads.
