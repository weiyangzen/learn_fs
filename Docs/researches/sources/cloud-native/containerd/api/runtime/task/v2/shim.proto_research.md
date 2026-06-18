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
