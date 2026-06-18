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
