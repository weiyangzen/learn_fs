# sources/cloud-native/containerd/api/events/task.pb.go

Purpose: generated Go protobuf bindings for container task lifecycle and exec events.

Important APIs/types/functions: exports `TaskCreate`, `TaskStart`, `TaskDelete`, `TaskIO`, `TaskExit`, `TaskOOM`, `TaskExecAdded`, `TaskExecStarted`, `TaskPaused`, `TaskResumed`, and `TaskCheckpointed`. Important fields include container IDs, bundle path, rootfs mounts, IO paths, checkpoint reference, PIDs, exit statuses, exec IDs, and `ExitedAt` timestamps. Getters are nil-safe and return zero values.

Control flow: generated code handles protobuf reflection, descriptor compression, and metadata registration. `TaskCreate` depends on `containerd.types.Mount` and nested `TaskIO`; delete/exit depend on protobuf timestamps. No task management behavior is implemented here.

State/persistence: no local state. Serialized messages are durable event payload contracts; field numbers and message names are API state.

Dependencies/integration: imports `github.com/containerd/containerd/api/types`, protobuf runtime/reflection, and timestamp types. Integrates with runtime task services, event streams, and consumers watching task state transitions.

Risks/test signals: task events have many fields where zero values can mean either unset or a real value, notably PID and exit status. `TaskDelete.ID` defaults to empty string to mean init exec, which consumers must interpret correctly. Tests should cover init exec versus named exec, rootfs mount serialization, timestamps, and checkpoint events.
