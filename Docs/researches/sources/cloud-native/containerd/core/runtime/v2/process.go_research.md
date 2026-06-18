# sources/cloud-native/containerd/core/runtime/v2/process.go

## Purpose
Implements `runtime.ExecProcess` for additional processes inside a shim-managed task and shared status conversion from task protobuf status to runtime status.

## APIs, Flow, State, Dependencies, Risks, And Tests
`process` holds an exec ID and parent `shimTask`. Methods translate runtime operations to shim task RPCs with `ExecID`: `Kill`, `State`, `ResizePty`, `CloseIO`, `Start`, `Wait`, and `Delete`. `statusFromProto` maps created/running/stopped/paused/pausing statuses to runtime statuses.

There is no local persistence; process state is retrieved from or mutated by the shim. RPC errors are converted with `errgrpc.ToNative`, and closed ttrpc connections map state lookup to `ErrNotFound`.

Dependencies include task v3 API, task status types, errdefs/errgrpc, ttrpc, runtime interfaces, and protobuf timestamp conversion. Integration is through `shimTask.Exec` and `shimTask.Process`.

Risks include an empty or wrong exec ID targeting the wrong process, unmapped status values becoming zero-value status, and differences between ttrpc closed errors and gRPC failures. Test signals include fake task-client tests for every method, error conversion checks, and lifecycle integration for exec start/wait/delete.
