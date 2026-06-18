<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto -->
# sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto

## Purpose
Defines the canonical protobuf contract for the containerd `Tasks` service. It describes how clients create and operate container tasks and exec processes through either gRPC or ttrpc generated bindings.

## Important APIs and Types
The `Tasks` service exposes unary RPCs: `Create`, `Start`, `Delete`, `DeleteProcess`, `Get`, `List`, `Kill`, `Exec`, `ResizePty`, `CloseIO`, `Pause`, `Resume`, `ListPids`, `Checkpoint`, `Update`, `Metrics`, and `Wait`. Key messages include `CreateTaskRequest` with rootfs mounts, stdio paths, checkpoint descriptor, runtime options, runtime path, and optional task API endpoint/version; `ExecProcessRequest` with process spec and exec ID; `DeleteResponse` and `WaitResponse` with exit status and `exited_at`; `CheckpointTaskResponse` with descriptors; and `MetricsResponse` with `types.Metric`.

## Control Flow
The proto expresses lifecycle ordering expected by callers: create a task, start it, optionally exec additional processes, manipulate IO/pty and pause/resume, query pids/metrics, wait for exit, then delete task/process state. The service itself is not implemented here.

## State and Persistence
Persistent or externally meaningful state is represented by container IDs, exec IDs, rootfs mounts, checkpoint descriptors, resource `Any` payloads, annotations, exit timestamps, and runtime endpoint configuration. The proto uses field numbers as the stable wire schema and leaves validation/persistence semantics to containerd services.

## Dependencies and Integration Points
Imports protobuf well-known types and containerd `types/descriptor.proto`, `types/metrics.proto`, `types/mount.proto`, and `types/task/task.proto`. Generated outputs integrate with gRPC and ttrpc transport files in the same package.

## Risks
Adding fields is generally safe, but reusing/removing field numbers or changing message meaning can break wire compatibility. `Any` payloads allow runtime-specific extensibility but create risk if type URLs or versions are not checked. `task_api_address` is powerful because it redirects task operations to another endpoint.

## Test Signals
Contract tests should assert generated bindings expose every RPC, validate wire compatibility for existing field numbers, and exercise task lifecycle integration through both transports.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/services/tasks/v1/tasks.proto -->
