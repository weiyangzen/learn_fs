# sources/cloud-native/containerd/api/runtime/task/v3/shim_grpc.pb.go

## Purpose

This generated `protoc-gen-go-grpc` file provides the gRPC transport binding for the `containerd.task.v3.Task` service. It is included only when the `no_grpc` build tag is not set. The file defines the gRPC client interface, server interface, default unimplemented server, registration function, unary handlers, and service descriptor.

## Important APIs, Types, and Functions

`TaskClient` exposes all 17 RPCs with `grpc.CallOption` variadics. `NewTaskClient` wraps a `grpc.ClientConnInterface` in `taskClient`; each method calls `cc.Invoke` with a full method path like `"/containerd.task.v3.Task/Create"`.

`TaskServer` is the implementation interface. It requires all RPC methods and `mustEmbedUnimplementedTaskServer` for forward compatibility. `UnimplementedTaskServer` returns `codes.Unimplemented` errors for every method and satisfies the embedding requirement. `UnsafeTaskServer` opts out of forward compatibility. `RegisterTaskServer` registers `Task_ServiceDesc`, which lists all unary methods, no streams, and metadata `runtime/task/v3/shim.proto`.

## Control Flow

Client calls allocate an output message, invoke the method on the connection, return the error if invocation fails, and otherwise return the output pointer. Server handlers allocate the concrete input, decode into it, call the service directly when no unary interceptor is configured, or construct `grpc.UnaryServerInfo` with the full method name and pass a typed handler through the interceptor.

## State and Persistence Behavior

The generated client stores only the gRPC connection interface. Handlers hold no durable state and allocate one request per call. All task lifecycle, IO, process, checkpoint, stats, and shutdown state is owned by the `TaskServer` implementation and the shim behind it.

## Dependencies and Integration Points

The file depends on `context`, `google.golang.org/grpc`, gRPC `codes` and `status`, and protobuf `emptypb`. It integrates with the v3 protobuf message types, with gRPC servers that expose containerd shim APIs, and with clients that prefer gRPC over ttrpc. The build tag allows builds to exclude gRPC code.

## Risks and Edge Cases

Builds using `no_grpc` will not include this API. Implementers must embed `UnimplementedTaskServer` or deliberately satisfy the unsafe opt-out path; otherwise forward-compatibility expectations can cause compile failures. The generated handlers rely on type assertions to `TaskServer` and specific request types. The binding has no validation or auth by itself; interceptors or implementations must enforce policy, deadlines, message limits, and observability.

## Test Signals

Useful signals include compiling both default and `no_grpc` builds, registering a fake server and exercising every client RPC, interceptor tests that assert full method names, unimplemented method tests for `codes.Unimplemented`, and integration tests that verify v3 gRPC clients interoperate with real shim servers.
