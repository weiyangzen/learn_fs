# sources/cloud-native/containerd/plugins/services/tasks/local.go

## Purpose
`local.go` implements the task service plugin that bridges API task requests to runtime v2 tasks, process operations, checkpoints, metrics, block I/O/RDT configuration, and deprecation warnings.

## Important APIs, Types, And Functions
The service plugin ID is `services.TasksService`. `Config` carries BlockIO and RDT config paths. `local` stores container metadata, content store, event publisher, task monitor, platform runtime, and warning service. Major methods implement the `api.TasksClient`: `Create`, `Start`, `Delete`, `DeleteProcess`, `Get`, `List`, `Pause`, `Resume`, `Kill`, `ListPids`, `Exec`, `ResizePty`, `CloseIO`, `Checkpoint`, `Update`, `Metrics`, and `Wait`. Helpers include `getProcessState`, `addTasks`, `getTasksMetrics`, `writeContent`, `getContainer`, `getTask`, `getTaskFromContainer`, `getCheckpointPath`, and `formatOptions`.

## Control Flow
Initialization resolves runtime v2, metadata, events, task monitor, and warning plugins, then monitors existing runtime tasks. `Create` loads the container, formats runtime options, handles checkpoint path/image restoration, builds `runtime.CreateOpts`, checks for existing tasks, creates the runtime task, starts monitoring it, and returns the PID. Process operations select either the init process or an exec process. Checkpointing writes checkpoint tar data and config into the content store when no direct image path is supplied. Metrics lists runtime tasks, filters them, and collects stats.

## State And Persistence
Container metadata is read from the metadata DB. Runtime task state is owned by the runtime plugin. Checkpoint artifacts may be extracted to temp runtime dirs and committed to the content store. Monitor registrations are in-memory but tied to task lifecycle. BlockIO/RDT global package config is set at startup.

## Dependencies And Integration Points
This service integrates metadata container store, content store, runtime v2, monitor, archive/content helpers, OCI descriptors, typeurl options, timeout configuration, deprecation warnings, filters, blockio, RDT, and protobuf conversion.

## Risks
Several operations commit side effects before later errors, such as runtime create before PID retrieval or checkpoint archive writes before descriptor response. Temp checkpoint directories created during `Create` from checkpoint image are not removed in this file. Typeurl option mismatches return errors tied to the runtime name. `getProcessState` uses a 2 second timeout and silently maps unknown statuses to `UNKNOWN` after logging.

## Test Signals
No task service tests are in this subset. Runtime integration tests, checkpoint tests, and deprecation-warning checks elsewhere are needed for coverage.
