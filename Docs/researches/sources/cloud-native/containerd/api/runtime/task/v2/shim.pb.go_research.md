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
