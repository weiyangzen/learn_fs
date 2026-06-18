<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.proto -->
# sources/cloud-native/containerd/api/types/task/task.proto

Purpose: source schema for process/task status data exposed by containerd task APIs.

Important APIs/types/functions: `Status` enum enumerates process lifecycle states. `Process` records container ID, process ID, pid, status, stdio paths, terminal flag, exit status, and exit timestamp. `ProcessInfo` carries pid plus platform-dependent extra info as `Any`.

Control flow: schema-only; status values define the external state machine vocabulary used by task service clients.

State/persistence: captures live or historical task/process state in task RPC responses/events. Stdio path fields are persisted long enough for clients to attach to FIFOs.

Dependencies/integration: imports protobuf `Any` and `Timestamp`; generated Go package is `api/types/task`. The client uses this schema in `container.Task` and `loadTask`.

Risks: clients must handle `UNKNOWN` and future enum values defensively. FIFO path values are host paths and may be absent, stale, or sensitive. Platform-specific `Any` needs clear type registration.

Test signals: generated bindings, task state transition events, attach/load behavior, and process-info platform payload round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/task/task.proto -->
