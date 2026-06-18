# sources/cloud-native/cri-o/internal/oci/runtime_vm.go

## Purpose
Implements CRI-O's VM/containerd-shim-v2 runtime path, aimed at Kata/VM-based containers where host PID assumptions differ from standard OCI.

## Important APIs and Control Flow
`runtimeVM` holds shim path/config, FIFO dir, exits path, ttrpc client/task service, runtime handler, and tracked `ContainerIO`. `newRuntimeVM` registers type URLs for OCI spec/process/resources. `CreateContainer` starts the shim daemon, creates FIFO-backed IO/loggers, builds `CreateTaskRequest`, optionally injects Kata guest-pull virtual-volume metadata, calls task `Create` with timeout, and records init PID. `StartContainer` starts the task and launches a wait goroutine that writes an exit marker and updates status. Exec flows through `execContainerCommon`: create exec FIFOs, attach streams, marshal process spec, task `Exec`, `Start`, resize, wait, timeout kill, and delete. `StopContainer` checks state, optionally sends stop signal, waits, then SIGKILLs with a fixed kill timeout. Status reconnects from bundle `address` if needed, reads task state, restores IO tracking, maps task status to CRI-O state, records exit code/PID, and marks OOM from bundle marker. Attach, log reopen, pause/unpause, update, low-level start/wait/kill/remove/resize/closeIO, and Kata virtual volume base64 encoding are also defined.

## State, Persistence, and Dependencies
Persists shim address/log files in the bundle, FIFO files under runtime root, CRI log output, exit markers in `ContainerExitsDir`, and bundle `oom` markers. Depends on containerd task v2/ttrpc/cio/fifo/typeurl/protobuf, Kata virtual volume types, OCI spec, CRI types, CRI-O logging/metrics/errdefs, and conmon timeout message constants for CRI-compatible exec-sync timeouts.

## Integration Points
Selected for handlers with `RuntimeTypeVM`. It uses `Container` state/locks/spec/log paths but deliberately avoids `Container.Living` for liveness because VM PID semantics differ. Linux stats are implemented in `runtime_vm_linux.go`; non-Linux stats are unsupported.

## Risks and Test Signals
Risks include shim connection lifecycle, cleanup after partial create, `ctrs` map consistency, nil `containerInfo` during forced cleanup, FIFO file leaks, timeout goroutines, error mapping from ttrpc/gRPC, guest-pull annotations, and unimplemented checkpoint/restore/serve streaming. No direct tests for this file appear in the subset.
