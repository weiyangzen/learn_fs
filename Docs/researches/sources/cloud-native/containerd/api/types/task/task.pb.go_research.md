<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.pb.go -->
# sources/cloud-native/containerd/api/types/task/task.pb.go

Purpose: generated Go binding for task process status and process-info messages.

Important APIs/types/functions: enum `Status` has `UNKNOWN`, `CREATED`, `RUNNING`, `STOPPED`, `PAUSED`, and `PAUSING` plus generated enum helpers. `Process` carries container/process IDs, pid, status, stdio FIFO paths, terminal flag, exit status, and `ExitedAt`. `ProcessInfo` carries pid plus platform-specific `Any` info.

Control flow: generated enum/message descriptor setup and nil-safe getters. It does not manage process lifecycle; lifecycle is implemented in task service/shims and surfaced through these messages.

State/persistence: serialized process state appears in task service responses and event payloads. FIFO path fields are used by client I/O attach code to reconstruct `cio.FIFOSet`.

Dependencies/integration: imports protobuf `Any` and `Timestamp`. `client/container.go` checks `Process.Status` before attaching existing IO and copies pid/status fields from task service responses.

Risks: `UNKNOWN` status intentionally suppresses IO attach in the client because FIFO paths may be absent. `ProcessInfo.Info` is platform-specific and requires consumer-specific decoding. PID and exit status are uint32, matching API conventions but not all host abstractions.

Test signals: task service/client tests should cover status transitions, attach behavior for `UNKNOWN`, timestamp conversion, and platform-specific `ProcessInfo` decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.pb.go -->
