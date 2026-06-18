# subset-b-000047 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim.pb.go -->
# sources/cloud-native/containerd/api/runtime/task/v2/shim.pb.go

## Purpose

This is generated `protoc-gen-go` output for `runtime/task/v2/shim.proto`. It materializes the `containerd.task.v2` shim task API as Go protobuf message types and a file descriptor. The API describes the task shim control surface used to create, start, inspect, pause, resume, checkpoint, kill, exec into, resize, update, wait on, collect stats for, connect to, and shut down shim-owned container tasks and exec processes.

## Important APIs, Types, and Functions

The file exports 27 protobuf message types: task lifecycle requests and responses such as `CreateTaskRequest`, `StartRequest`, `DeleteResponse`, `StateResponse`, `WaitResponse`, `StatsResponse`, `ConnectResponse`, plus simple operation requests such as `KillRequest`, `CloseIORequest`, `PauseRequest`, and `ResumeRequest`. Every message has generated `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` accessors. `UpdateTaskRequest` includes a `map[string]string` `Annotations` field represented in the descriptor by an `AnnotationsEntry` map entry.

The descriptor surface is `File_runtime_task_v2_shim_proto`, `file_runtime_task_v2_shim_proto_rawDescGZIP`, `file_runtime_task_v2_shim_proto_msgTypes`, `file_runtime_task_v2_shim_proto_goTypes`, `file_runtime_task_v2_shim_proto_depIdxs`, and `file_runtime_task_v2_shim_proto_init`. These bind message types, dependency indexes, the `Task` service schema, and reflection metadata.

## Control Flow

Message methods are simple generated accessors. `Reset` zeroes the receiver and stores message info when unsafe protobuf support is enabled. `ProtoReflect` returns the cached message state when possible or falls back to the message info object. Getter methods return zero values for nil receivers.

Initialization is the main control-flow block. `init` calls `file_runtime_task_v2_shim_proto_init`, which exits early if the file descriptor already exists, assigns exporter functions when `protoimpl.UnsafeEnabled` is false, then builds a `protoimpl.TypeBuilder` with 27 messages and one service. The raw descriptor is compressed once through `sync.Once` and cleared after descriptor construction.

## State and Persistence Behavior

The file owns only in-memory protobuf state: `protoimpl.MessageState`, `SizeCache`, `UnknownFields`, and typed message fields. It does not persist container state or perform shim operations. It does encode the API's state contract: task IDs, exec IDs, bundle paths, rootfs mounts, IO paths, terminal flags, checkpoint paths, PIDs, exit statuses, `exited_at` timestamps, task status enum values, process info slices, resource updates, annotations, stats payloads, and shim/task PID connection metadata.

## Dependencies and Integration Points

The generated types depend on `github.com/containerd/containerd/api/types` for `Mount`, `github.com/containerd/containerd/api/types/task` for `Status` and `ProcessInfo`, and protobuf runtime packages for reflection, `Any`, `Empty`, and `Timestamp`. The service schema is consumed by the v2 ttrpc bindings in `shim_ttrpc.pb.go` and by shim/client implementations that exchange these protobuf messages.

## Risks and Edge Cases

Manual edits are fragile because this file must remain in sync with `shim.proto`. The nil-safe getters can hide absent nested data by returning zero values. `Any` fields for options, specs, resources, and stats are opaque here; validation and type interpretation must happen in callers. Map serialization order for annotations is not a semantic guarantee. Package and service names include `v2`, so accidentally mixing v2 and v3 message or service names can break compatibility even where schemas look identical.

## Test Signals

Useful signals are generated-code compilation, reproducible regeneration from `shim.proto`, descriptor reflection tests for service and field indexes, protobuf round-trip tests for every message type, and shim integration tests that exercise create/start/wait/delete plus exec, IO, stats, and update flows through the v2 transport.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim.proto -->
# sources/cloud-native/containerd/api/runtime/task/v2/shim.proto

## Purpose

This proto file defines the `containerd.task.v2.Task` shim service contract. A shim is launched per container, owns container and exec-process IO, parents the container process, and allows clients to reconnect to IO and observe exit state. The schema is the source of truth for the generated Go protobuf and ttrpc bindings in this package.

## Important APIs, Types, and Functions

The `Task` service exposes unary RPCs: `State`, `Create`, `Start`, `Delete`, `Pids`, `Pause`, `Resume`, `Checkpoint`, `Kill`, `Exec`, `ResizePty`, `CloseIO`, `Update`, `Wait`, `Stats`, `Connect`, and `Shutdown`. Response-less operations return `google.protobuf.Empty`.

Core messages include `CreateTaskRequest` with ID, bundle, rootfs mounts, IO paths, checkpoint lineage, terminal mode, and runtime options; `ExecProcessRequest` with exec ID, IO paths, terminal flag, and packed process spec; `StateResponse` with task identity, bundle, PID, status, IO fields, terminal flag, exit status, timestamp, and exec ID; `DeleteResponse` and `WaitResponse` with exit status and time; `PidsResponse` with `ProcessInfo` entries; `UpdateTaskRequest` with packed resources and annotations; `StatsResponse` with packed stats; and `ConnectResponse` with shim PID, task PID, and version.

## Control Flow

The proto file has no executable control flow, but it defines the valid RPC lifecycle. A typical caller creates a task, starts it, observes state or PIDs, waits for exit, then deletes it. Additional exec processes are created through `Exec`, started through `Start` with `exec_id`, waited on through `Wait`, and deleted by `Delete` with the same exec ID. Mutation calls such as `Pause`, `Resume`, `Kill`, `CloseIO`, `ResizePty`, `Checkpoint`, and `Update` target a task ID and sometimes an exec ID.

## State and Persistence Behavior

The schema models state exchanged with a shim rather than storing it. Persistent or durable behavior is implementation-defined in shim code. The contract carries enough state to reconstruct task/process status, IO endpoints, exit results, process lists, checkpoint paths, resource updates, annotations, stats, and connection metadata. `google.protobuf.Any` is intentionally used for runtime-specific options, specs, resource payloads, and stats.

## Dependencies and Integration Points

Imports are `google/protobuf/any.proto`, `empty.proto`, `timestamp.proto`, `types/mount.proto`, and `types/task/task.proto`. The `go_package` maps generated Go code to `github.com/containerd/containerd/api/runtime/task/v2;task`. It integrates with runtime shim implementations, ttrpc clients, containerd task management code, and the common containerd API types for mounts, process info, and status values.

## Risks and Edge Cases

The contract has no explicit validation rules for IDs, paths, terminal/IO combinations, signal values, or packed `Any` type URLs, so implementations must validate these. `exec_id` is optional by convention and changes the target from init process to exec process; mishandling an empty versus non-empty exec ID can affect the wrong process. API evolution must preserve field numbers and wire compatibility. `ShutdownRequest.now` is a sharp semantic flag whose exact cleanup behavior lives outside the schema.

## Test Signals

Good signals include generated binding diffs after schema changes, compatibility tests that old clients can talk to new shims, lifecycle integration tests for init and exec processes, checkpoint/update/stats type unpacking tests, and negative tests for invalid IDs, IO paths, malformed `Any` payloads, and unsupported signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/runtime/task/v2/shim_ttrpc.pb.go

## Purpose

This generated `protoc-gen-go-ttrpc` file adapts the `containerd.task.v2.Task` service to containerd's ttrpc transport. It defines the server-side interface, registers unary method handlers on a ttrpc server, and provides a client implementation that issues calls with the v2 service name.

## Important APIs, Types, and Functions

`TTRPCTaskService` is the service implementation interface. It mirrors the proto RPCs and returns typed protobuf responses or `*emptypb.Empty` for empty responses. `RegisterTTRPCTaskService` installs the service under `"containerd.task.v2.Task"` with a `ttrpc.ServiceDesc` containing a method map for all 17 RPCs. `NewTTRPCTaskClient` returns a `TTRPCTaskService` backed by `ttrpctaskClient`, whose methods call `client.Call` with the service and method names.

## Control Flow

Server registration builds one closure per RPC. Each closure allocates the concrete request type, invokes the transport `unmarshal` callback into that request, returns the unmarshal error if decoding fails, and otherwise dispatches to the corresponding service method with the request pointer.

Client methods allocate a concrete response value, call `c.client.Call(ctx, "containerd.task.v2.Task", "<Method>", req, &resp)`, return the call error if any, and otherwise return the response pointer. There is no streaming control flow and no generated middleware/interceptor layer in this ttrpc binding.

## State and Persistence Behavior

This file keeps no persistent state. The only stored state is the `*ttrpc.Client` pointer inside `ttrpctaskClient`. Per-call request and response values are stack/local allocations. Actual task state, process lifecycle, IO ownership, checkpoints, stats, and shutdown behavior are delegated to the implementation behind `TTRPCTaskService`.

## Dependencies and Integration Points

The file depends on `context`, `github.com/containerd/ttrpc`, and `google.golang.org/protobuf/types/known/emptypb`. It integrates with the v2 message types in `shim.pb.go`, with ttrpc servers in shim processes, and with containerd clients that communicate with shims over ttrpc sockets.

## Risks and Edge Cases

Service and method names are string literals; v2 clients must use `"containerd.task.v2.Task"` and cannot talk to v3 by accident. Nil service or nil client values would panic or fail at runtime because there are no generated guards. Request validation is absent, so decoded but semantically invalid protobufs reach the service implementation. The generated binding does not expose interceptors; cross-cutting concerns such as auth, logging, tracing, deadlines, and size limits must be handled by ttrpc setup or the implementation.

## Test Signals

Useful tests register a fake `TTRPCTaskService`, call each generated client method, and assert the expected method name, request type, response type, and error propagation. Additional signals are compile-time interface conformance, malformed request decode tests, context cancellation/deadline behavior through `client.Call`, and integration tests against a real shim ttrpc server.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v2/shim_ttrpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/doc.go -->
# sources/cloud-native/containerd/api/runtime/task/v3/doc.go

## Purpose

This small Go source file declares package `task` for the v3 runtime task API directory and carries the containerd copyright and Apache 2.0 license header. It does not add package documentation text beyond the package declaration.

## Important APIs, Types, and Functions

There are no exported APIs, types, functions, constants, or variables. The only executable Go syntax is `package task`.

## Control Flow

There is no control flow. The file participates only in package compilation.

## State and Persistence Behavior

The file has no state and no persistence behavior. Runtime task state is represented in the generated v3 protobuf and transport files, not here.

## Dependencies and Integration Points

There are no imports. Its integration point is the Go package system: it is compiled with the other files in `api/runtime/task/v3` and helps establish the package even though the generated files carry most of the implementation surface.

## Risks and Edge Cases

Despite being named `doc.go`, the file does not provide a package comment. That means Go documentation consumers get no human-authored package overview from this file. Any package-level explanatory documentation must be added deliberately and kept consistent with the generated proto contract.

## Test Signals

Compilation is the only meaningful signal. Documentation checks could flag the absence of a package comment if this repository enforces exported package documentation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim.pb.go -->
# sources/cloud-native/containerd/api/runtime/task/v3/shim.pb.go

## Purpose

This is generated `protoc-gen-go` output for `runtime/task/v3/shim.proto`. It exposes the `containerd.task.v3` shim task API as Go protobuf message structs and reflection metadata. The schema is effectively the v3 package version of the task shim lifecycle contract, while transport bindings are supplied by adjacent gRPC and ttrpc generated files.

## Important APIs, Types, and Functions

The exported message set matches the v3 proto: `CreateTaskRequest`, `CreateTaskResponse`, `DeleteRequest`, `DeleteResponse`, `ExecProcessRequest`, `ExecProcessResponse`, `ResizePtyRequest`, `StateRequest`, `StateResponse`, `KillRequest`, `CloseIORequest`, `PidsRequest`, `PidsResponse`, `CheckpointTaskRequest`, `UpdateTaskRequest`, `StartRequest`, `StartResponse`, `WaitRequest`, `WaitResponse`, `StatsRequest`, `StatsResponse`, `ConnectRequest`, `ConnectResponse`, `ShutdownRequest`, `PauseRequest`, and `ResumeRequest`. Each has standard generated protobuf methods and nil-safe getters.

The descriptor entry point is `File_runtime_task_v3_shim_proto`. Supporting internals include the raw descriptor, one-time GZIP compression, message info array, Go type array, dependency indexes, exporter callbacks for non-unsafe protobuf mode, and the `protoimpl.TypeBuilder` call that finalizes reflection data.

## Control Flow

Per-message methods are generated boilerplate: reset to zero, expose string and reflection forms, and return field values or defaults. Descriptor control flow is guarded by a nil check and `sync.Once` compression. During init, the builder records 27 messages and one service, wires field and RPC type dependencies, then drops raw descriptor and type slices to reduce retained initialization data.

## State and Persistence Behavior

The file keeps only protobuf runtime state in message instances. It does not run tasks, store checkpoints, manage IO, or maintain process state. Its fields carry the API's state snapshots and mutation inputs, including task IDs, exec IDs, mount lists, IO endpoints, terminal flags, options/spec/resources/stats `Any` payloads, annotations maps, PIDs, status enum values, process info lists, exit timestamps, and shim version metadata.

## Dependencies and Integration Points

Dependencies are the same shape as v2 but with the v3 package descriptor: containerd `types.Mount`, task `Status` and `ProcessInfo`, protobuf reflection/runtime packages, `Any`, `Empty`, and `Timestamp`. The generated descriptor integrates with `shim_grpc.pb.go` and `shim_ttrpc.pb.go`, and with any code using protobuf reflection or marshaling for the v3 task API.

## Risks and Edge Cases

The v3 generated schema is textually very close to v2 in this snapshot but has distinct package, descriptor, and service names. Mixing versions at transport boundaries will fail even if message fields look equivalent. Opaque `Any` fields require caller-side type checks. Nil-safe getters and proto3 zero values make absent and explicitly zero scalar values indistinguishable. Manual edits should be avoided because regeneration will replace them.

## Test Signals

Signals include package compilation with and without the gRPC build tag, reproducible generation from `shim.proto`, descriptor reflection checks for `containerd.task.v3`, protobuf round trips for every message, annotation map coverage, and integration tests that run the v3 task lifecycle through both gRPC and ttrpc bindings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim.proto -->
# sources/cloud-native/containerd/api/runtime/task/v3/shim.proto

## Purpose

This proto file defines the `containerd.task.v3.Task` shim service contract. It describes the RPC API for a per-container shim that owns task and exec-process IO, parents container processes, supports reconnection, and reports exit status. The file is the source for the v3 Go protobuf, gRPC, and ttrpc generated bindings.

## Important APIs, Types, and Functions

The `Task` service defines unary RPCs for task lifecycle and process control: `State`, `Create`, `Start`, `Delete`, `Pids`, `Pause`, `Resume`, `Checkpoint`, `Kill`, `Exec`, `ResizePty`, `CloseIO`, `Update`, `Wait`, `Stats`, `Connect`, and `Shutdown`.

Messages mirror the operation set. `CreateTaskRequest` carries container identity, bundle path, rootfs mounts, terminal and IO settings, checkpoint inputs, and runtime options. `ExecProcessRequest` carries exec ID, IO settings, terminal mode, and a packed spec. State and exit messages expose PIDs, status, exit code, and `Timestamp` values. `UpdateTaskRequest` carries resources and annotations. `StatsResponse` and request option/spec/resource fields use `Any` so runtime-specific payloads can be carried without changing this schema.

## Control Flow

There is no executable control flow in the proto file, but it encodes the task API sequence. Initial task operations generally flow through `Create`, `Start`, status inspection, `Wait`, and `Delete`. Exec processes are added with `Exec`, started with `Start` using `exec_id`, observed with `State` or `Wait`, and deleted through `Delete`. Operational mutations are explicit unary calls for pause/resume, signal delivery, IO close, pty resize, checkpoint, resource update, stats, reconnect, and shutdown.

## State and Persistence Behavior

The proto defines exchanged state, not storage. It models task state snapshots, process lists, exit results, IO paths, annotations, resource updates, checkpoint paths, and connection metadata. Durability, checkpoint writing, cleanup, and process supervision semantics live in shim implementations.

## Dependencies and Integration Points

Imports include protobuf `Any`, `Empty`, and `Timestamp`, plus containerd `types/mount.proto` and `types/task/task.proto`. `go_package` points to `github.com/containerd/containerd/api/runtime/task/v3;task`. It integrates with generated gRPC and ttrpc code in this directory, containerd runtime clients, and shim service implementations that implement the v3 API.

## Risks and Edge Cases

The schema relies on implementation conventions for empty `exec_id`, valid IO paths, signal values, checkpoint paths, and `Any` type URLs. Field numbers are compatibility-critical. Although the schema currently aligns closely with v2, the package and service name are v3-specific; compatibility must be judged at the transport and generated-package level, not just by visual field similarity. Shutdown immediacy and update semantics are intentionally not fully specified here.

## Test Signals

Important signals are generation diffs, protobuf descriptor compatibility checks, transport-level lifecycle tests for both gRPC and ttrpc, tests for packed option/spec/resource/stats payloads, and negative tests around bad IDs, exec IDs, paths, and unsupported runtime options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim_grpc.pb.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim_ttrpc.pb.go -->
# sources/cloud-native/containerd/api/runtime/task/v3/shim_ttrpc.pb.go

## Purpose

This generated `protoc-gen-go-ttrpc` file provides the ttrpc binding for the `containerd.task.v3.Task` shim service. It mirrors the v3 proto RPC set as a Go interface, registers method handlers on a ttrpc server, and provides a client implementation that calls the v3 ttrpc service name.

## Important APIs, Types, and Functions

`TTRPCTaskService` lists all task RPCs with typed protobuf request and response pointers. `RegisterTTRPCTaskService` registers service `"containerd.task.v3.Task"` and installs a `map[string]ttrpc.Method` containing handlers for `State`, `Create`, `Start`, `Delete`, `Pids`, `Pause`, `Resume`, `Checkpoint`, `Kill`, `Exec`, `ResizePty`, `CloseIO`, `Update`, `Wait`, `Stats`, `Connect`, and `Shutdown`. `NewTTRPCTaskClient` creates `ttrpctaskClient`, and each client method invokes `client.Call` with the v3 service name and method string.

## Control Flow

Each server method closure creates the right request struct, calls the provided unmarshal function, returns any decode error, and delegates to the matching service method. Each client method creates a response struct, calls the ttrpc client, returns errors unchanged, and returns the response pointer on success. There are no streams and no generated interceptors.

## State and Persistence Behavior

Only the `*ttrpc.Client` pointer is retained by the generated client. All request/response objects are per-call values. Durable task state, process supervision, IO, checkpointing, resource updates, and shutdown behavior are outside this binding and live in the service implementation.

## Dependencies and Integration Points

Dependencies are `context`, `github.com/containerd/ttrpc`, and protobuf `emptypb`. The binding integrates with v3 protobuf message types and with shim servers that expose v3 task APIs over ttrpc. It coexists with the v3 gRPC binding, giving the same schema two transport surfaces.

## Risks and Edge Cases

The v3 service name is a string literal and must match on both client and server. Version confusion with v2 is easy because method and message shapes are similar. No generated validation prevents nil clients, nil services, invalid decoded requests, missing deadlines, or oversized messages. Transport-level concerns such as tracing and authorization must be configured outside this generated file.

## Test Signals

Good signals include fake-service tests for every method, service-name assertions, error propagation tests from unmarshal and `client.Call`, context cancellation tests, and end-to-end shim tests that compare v3 ttrpc behavior with the gRPC binding for the same lifecycle operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/runtime/task/v3/shim_ttrpc.pb.go -->
