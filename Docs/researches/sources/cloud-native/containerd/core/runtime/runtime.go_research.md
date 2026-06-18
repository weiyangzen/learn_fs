<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/runtime.go -->
# sources/cloud-native/containerd/core/runtime/runtime.go

## Purpose
Defines core runtime task creation options, process IO descriptors, exit information, and the platform runtime interface.

## Important APIs, Types, And Functions
- `IO` describes stdin/stdout/stderr paths and terminal mode.
- `CreateOpts` carries OCI spec, rootfs mounts, IO, checkpoint/restore flags, runtime options, task options, runtime name/path, sandbox ID, task API address, and version.
- `Exit` records PID, exit status, and timestamp.
- `PlatformRuntime` defines `ID`, `Create`, `Get`, `Tasks`, and `Delete`.

## Control Flow
This file is interface/data-model only. Runtime implementations consume `CreateOpts` and return `Task` objects; managers use `PlatformRuntime` for lifecycle operations.

## State And Persistence
No state is stored here. Struct fields are passed between services and runtime implementations.

## Dependencies And Integration Points
Depends on containerd mount types and typeurl for opaque runtime/spec options. Used by runtime v1/v2 managers and task services.

## Risks And Edge Cases
Several fields are opaque `typeurl.Any`, so correctness depends on type registration and runtime-specific decoding. `Runtime` can be a named runtime or absolute binary path, which affects shim launch logic.

## Test Signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/runtime.go -->
