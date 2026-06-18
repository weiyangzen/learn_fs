# sources/cloud-native/soci-snapshotter/benchmark/framework/containerd_utils.go

Purpose: framework utilities for starting/stopping containerd and driving container lifecycle operations during benchmarks.

Important APIs/types/functions: `ContainerdProcess`, `StartContainerd`, `StopProcess`, `PullImage`, `DeleteImage`, `CreateContainer`, `TaskDetails`, `CreateTask`, `RunContainerTaskForReadyLine`, `GetRemoteOpts`, `GetTestContext`, and `newClient`.

Control flow: `StartContainerd` launches a containerd subprocess with custom address/root/state/config and opens log files, then creates a client. Lifecycle helpers create containers/tasks with unique IDs, attach pipes, start tasks, watch stdout/stderr for a ready line or process exit/timeout, and provide cleanup closures that kill/delete tasks and remove roots/state/sockets.

State and persistence: creates `/tmp` roots/state/sockets and output log files, then removes them on stop. It also sets containerd namespace and logging context.

Dependencies/integration: used by all benchmark workloads; depends on containerd v2 client, cio, namespaces, logrus, and host `containerd` binary.

Risks: `StopProcess` kills without waiting. Timeout path in `RunContainerTaskForReadyLine` returns nil error even if ready line never appears. Pipe scanner goroutines may outlive briefly until cleanup closes pipes.

Test signals: benchmark success and absence of leftover processes/state; targeted tests should validate timeout semantics.
