# sources/cloud-native/cri-o/internal/oci/runtime_pod.go

## Purpose
Implements the pod-level conmon-rs runtime adapter. It manages a conmon-rs server per pod/infra container while delegating much OCI behavior to an embedded `runtimeOCI`.

## Important APIs and Control Flow
`newRuntimePod` returns the infra container's runtime for workload containers by looking up the sandbox implementation; for infra containers it configures a conmon-rs client with runtime path/root, cgroup manager, tracing, log driver, and heaptrack options parsed from monitor env. `CreateContainer` moves the conmon-rs process to the desired cgroup for infra/spoofed containers, creates the container through conmon-rs, records init PID and monitor process start time. Most lifecycle methods delegate to embedded OCI behavior. `ExecSyncContainer`, `AttachContainer`, `ReopenContainerLog`, `ServeExecContainer`, and `ServeAttachContainer` use conmon-rs RPCs directly. Deleting the infra container shuts down the conmon-rs client.

## State, Dependencies, and Integration
State is shared with `Container`; server files and attach sockets live under the pod server directory. Depends on `github.com/containers/conmon-rs/pkg/client`, CRI-O tracing/config/logging, Podman resize utilities, and conmon timeout constants. Selected when a handler has `RuntimeTypePod`.

## Risks and Test Signals
The non-infra lookup panics if the sandbox runtime was not created first. Environment parsing accepts only known key/value options. The hybrid delegation means conmon-rs and OCI assumptions must stay compatible for status, stop, and checkpoint paths. No direct tests for this file are in the subset.
