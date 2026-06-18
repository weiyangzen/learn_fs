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
