<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go -->
# sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go

Purpose: implements the Docker plugin executor using containerd/libcontainerd containers and tasks.

Important APIs and types: `ExitHandler`, `Executor`, `c8dPlugin`, `New`, `Create`, `Restore`, `IsRunning`, `Signal`, `ProcessEvent`, `deleteTaskAndContainer`, `rio`, and `attachStreamsFunc`.

Control flow: `New` creates a libcontainerd remote client with the executor as backend. `Create` replaces any stale plugin container, creates a task with stdout/stderr attachment, starts it, and stores plugin state. `Restore` loads an existing container, attaches to its task, checks status, cleans up stopped/missing tasks, and stores live state. `ProcessEvent` handles only exit events: it deletes task/container resources and delegates to `ExitHandler`.

State and persistence: in-memory `plugins` map tracks active plugin ID to container/task handles under mutex. Actual plugin runtime state persists in containerd until cleanup.

Dependencies and integration: depends on containerd client/cio, libcontainerd replace/client/types, Docker errdefs, plugin exit handling, and OCI specs.

Risks: `attachStreamsFunc` panics if stdin exists because plugin stdin should never be created. `ProcessEvent` calls exit handler even for unknown plugin exits. `Create` stores plugin only after task start, so early exit events could race with insertion.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/plugin/executor/containerd/containerd.go -->
