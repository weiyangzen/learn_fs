<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go

Purpose: implements the remote containerd-backed libcontainerd client used by the daemon. It wraps containerd client/container/task/process APIs, adapts Docker event semantics, manages bundle paths and stdio I/O, and handles checkpoint content transfer.

Important APIs and types: `client`, `container`, `task`, and `process` wrap containerd objects. Key functions include `NewClient`, `Version`, `NewContainer`, `LoadContainer`, `AttachTask`, `NewTask`, `Start`, `Exec`, `Kill`, `Pause`, `Resume`, `Stats`, `Summary`, `Delete`, `ForceDelete`, `Status`, `CreateCheckpoint`, `Task`, `createIO`, `closeStdin`, `processEventStream`, `writeContent`, and `bundleDir`. The `DockerContainerBundlePath` label links container metadata to the bundle directory.

Control flow: `NewClient` stores the underlying containerd client and starts an event subscription goroutine. `NewContainer` composes containerd options for spec, runtime, and bundle label creation. `NewTask` optionally uploads a checkpoint tar to the content store, reads container metadata/spec without refreshed metadata, builds platform FIFO/named-pipe config, creates I/O, and creates the task with checkpoint and platform options. `Exec` builds I/O for a secondary process, registers and starts it, and deletes the exec process if start fails. `Stats` and `Summary` convert typeurl metrics/process info into daemon types. `CreateCheckpoint` asks containerd for a checkpoint image, reads the checkpoint descriptor from content, applies it to a directory, and deletes the temporary image. Event stream handling subscribes to task topics in the namespace and converts create/start/exit/OOM/exec/pause/resume events into backend callbacks through `queue.Queue`.

State and persistence: state includes containerd metadata, bundle directories under `stateDir`, temporary checkpoint content/images, and in-memory event queue state. Delete removes the bundle directory unless `LIBCONTAINERD_NOCLEAN=1`. Stdin close synchronization uses a channel because the process object may not exist when the I/O writer is closed.

Dependencies and integration: depends on containerd client/content/images/archive/cio APIs, OCI specs, runc options, typeurl/protobuf, OpenTelemetry spans, Docker errdefs, and the backend event interface. Platform files provide `WithBundle`, FIFO construction, direct I/O, summary conversion, log-level options, and resource updates.

Risks: it assumes container labels and spec do not change between container creation and task/exec operations by using `WithoutRefreshedMetadata`. Event stream restart logic depends on `IsServing` and can duplicate subscriptions only by starting a new goroutine after failure. Temporary checkpoint cleanup is best-effort. `createIO` has subtle stdin-close races and intentionally ignores "transport is closing" errors. Bundle cleanup relies on the label value.

Test signals: no direct tests in this subset. Integration is exercised through daemon/containerd tests elsewhere; platform-specific unit coverage is absent here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/remote/client.go -->
