# sources/distributed-fs/beegfs-protobuf/go/flex/flex_grpc.pb.go

## Purpose

This generated Go file is the gRPC binding for the `flex.WorkerNode` service declared in `flex.proto`, produced by `protoc-gen-go-grpc v1.5.1`. It exposes typed client and server interfaces over the protobuf messages defined in `flex.pb.go`. The service models a worker node that accepts configuration, reports readiness, receives work, updates work state, supports bulk work-state operations, and advertises capabilities.

The file contains transport glue only: it does not implement worker behavior, persistence, validation, scheduling, or transfer logic. Those responsibilities belong to code that implements `WorkerNodeServer` or calls `WorkerNodeClient`.

## Important APIs, Types, And Functions

The package-level compatibility constant `grpc.SupportPackageIsVersion9` requires gRPC-Go v1.64.0 or later.

Full method-name constants define the canonical unary RPC paths:

- `WorkerNode_UpdateConfig_FullMethodName`: `/flex.WorkerNode/UpdateConfig`
- `WorkerNode_Heartbeat_FullMethodName`: `/flex.WorkerNode/Heartbeat`
- `WorkerNode_SubmitWork_FullMethodName`: `/flex.WorkerNode/SubmitWork`
- `WorkerNode_UpdateWork_FullMethodName`: `/flex.WorkerNode/UpdateWork`
- `WorkerNode_BulkUpdateWork_FullMethodName`: `/flex.WorkerNode/BulkUpdateWork`
- `WorkerNode_GetCapabilities_FullMethodName`: `/flex.WorkerNode/GetCapabilities`

`WorkerNodeClient` is the typed client interface:

- `UpdateConfig(context.Context, *UpdateConfigRequest, ...grpc.CallOption) (*UpdateConfigResponse, error)`
- `Heartbeat(context.Context, *HeartbeatRequest, ...grpc.CallOption) (*HeartbeatResponse, error)`
- `SubmitWork(context.Context, *SubmitWorkRequest, ...grpc.CallOption) (*SubmitWorkResponse, error)`
- `UpdateWork(context.Context, *UpdateWorkRequest, ...grpc.CallOption) (*UpdateWorkResponse, error)`
- `BulkUpdateWork(context.Context, *BulkUpdateWorkRequest, ...grpc.CallOption) (*BulkUpdateWorkResponse, error)`
- `GetCapabilities(context.Context, *GetCapabilitiesRequest, ...grpc.CallOption) (*GetCapabilitiesResponse, error)`

`NewWorkerNodeClient` wraps a `grpc.ClientConnInterface` in the unexported `workerNodeClient`. Each client method prepends `grpc.StaticMethod()` to call options, allocates the typed response, invokes the full method name through `cc.Invoke`, returns the response on success, and returns nil plus the transport error on failure.

`WorkerNodeServer` is the implementation interface. It mirrors the six unary methods and includes `mustEmbedUnimplementedWorkerNodeServer()` to enforce forward-compatible embedding.

`UnimplementedWorkerNodeServer` provides default methods that return `codes.Unimplemented` errors through `status.Errorf`. Generated comments recommend embedding it by value to avoid nil-pointer panics when future unimplemented methods are invoked.

`UnsafeWorkerNodeServer` allows an implementation to opt out of forward compatibility by satisfying only `mustEmbedUnimplementedWorkerNodeServer()`, but the generated comment warns that newly added methods will become compile-time breaks.

`RegisterWorkerNodeServer` validates by-value embedding when available, then registers `WorkerNode_ServiceDesc` with a `grpc.ServiceRegistrar`.

Private unary handler functions (`_WorkerNode_UpdateConfig_Handler`, `_WorkerNode_Heartbeat_Handler`, `_WorkerNode_SubmitWork_Handler`, `_WorkerNode_UpdateWork_Handler`, `_WorkerNode_BulkUpdateWork_Handler`, and `_WorkerNode_GetCapabilities_Handler`) decode incoming requests, call the server implementation directly when no interceptor is present, or wrap the call in `grpc.UnaryServerInfo` and an interceptor handler.

`WorkerNode_ServiceDesc` declares service name `flex.WorkerNode`, the server handler type, all six unary method descriptors, no streams, and metadata `flex.proto`.

## Control Flow

Client-side control flow for every method is identical:

1. Start with `grpc.StaticMethod()` and append user-supplied call options.
2. Allocate the expected response message.
3. Call `ClientConnInterface.Invoke(ctx, fullMethodName, request, response, options...)`.
4. Return the populated response or the encountered error.

Server-side handler flow for every unary RPC is:

1. Allocate the expected request message.
2. Decode the inbound message with the provided decoder.
3. If decode fails, return the decode error.
4. If no unary interceptor is configured, type-assert `srv` to `WorkerNodeServer` and call the matching method.
5. If an interceptor exists, create `grpc.UnaryServerInfo` with the full method name and a closure that type-asserts the request, then pass control to the interceptor.

Registration flow calls `testEmbeddedByValue()` if the server implementation exposes it through the embedded unimplemented server. This intentionally panics early if `UnimplementedWorkerNodeServer` was embedded as a nil pointer, preventing a later runtime panic during an unimplemented method call.

## State And Persistence Behavior

This file has no persistent state. It defines stateless client stubs, server registration metadata, and per-call request/response allocation. Request cancellation, deadlines, authentication metadata, retries, and transport behavior flow through `context.Context`, `grpc.CallOption`, interceptors, and gRPC configuration supplied by callers.

The RPCs move domain state represented by `flex.pb.go` messages:

- `UpdateConfig` carries desired worker configuration.
- `Heartbeat` observes readiness and optional node statistics.
- `SubmitWork` assigns a unit of work and receives the worker's accepted status.
- `UpdateWork` requests a specific work-state change, such as cancellation.
- `BulkUpdateWork` handles node-wide outstanding work behavior during connection or drain/removal flows.
- `GetCapabilities` discovers worker build and feature metadata.

## Dependencies

Direct imports are:

- `context` from the standard library.
- `google.golang.org/grpc` for client connections, service registration, method descriptors, interceptors, and call options.
- `google.golang.org/grpc/codes` and `google.golang.org/grpc/status` for default unimplemented server errors.

All request and response message types come from the same `flex` package and are generated in `flex.pb.go`.

## Integration Points

This file integrates generated protobuf messages with the gRPC runtime:

- Clients use `NewWorkerNodeClient` with any `grpc.ClientConnInterface`.
- Servers implement `WorkerNodeServer`, usually embed `UnimplementedWorkerNodeServer` by value, and call `RegisterWorkerNodeServer`.
- Interceptors can observe and control all RPCs through full method names and typed request objects.
- `WorkerNode_ServiceDesc` supports direct registration by gRPC and service reflection/introspection tools.
- The service method list matches dependency indexes embedded in `flex.pb.go`, which record one service with six unary methods.

## Risks

- Manual edits are generated-code drift and will be overwritten by `protoc-gen-go-grpc`.
- Server implementations must embed `UnimplementedWorkerNodeServer` by value for forward compatibility; embedding it as a nil pointer can cause an intentional registration-time panic.
- Client methods return nil response plus error on transport failure; callers must not dereference response values before checking errors.
- Handler functions use type assertions to `WorkerNodeServer` and concrete request types. Misregistration or incorrect manual use of handlers will panic.
- There are no streaming RPCs, so long-running work status updates must be modeled through unary calls and returned `Work` messages rather than a persistent stream.
- The generated stubs do not enforce semantic validation such as allowed work-state transitions, configuration completeness, credential secrecy, or RST/job compatibility.
- The `grpc.StaticMethod()` call option marks methods as static for gRPC internals; custom call-option logic should account for it being prepended before caller-supplied options.

## Test Signals

Useful validation should focus on integration behavior:

- Compile tests that generated `flex.pb.go` and `flex_grpc.pb.go` are in sync with `flex.proto`.
- A fake `WorkerNodeServer` registered on a bufconn or test gRPC server, with client calls for all six methods.
- Interceptor tests verifying full method names and typed request dispatch.
- Forward-compatibility tests or static checks ensuring server implementations embed `UnimplementedWorkerNodeServer` by value.
- Error-path tests for unimplemented default methods returning `codes.Unimplemented`.
- Caller tests that check errors before response dereference for all client methods.
