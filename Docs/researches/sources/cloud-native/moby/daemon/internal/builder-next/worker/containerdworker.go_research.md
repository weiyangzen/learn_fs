# sources/cloud-native/moby/daemon/internal/builder-next/worker/containerdworker.go

## Purpose
Adapts BuildKit's base containerd worker for Docker's containerd image store mode.

## APIs, Control Flow, and Integration
`ContainerdWorker` embeds `*base.Worker` and stores export callbacks. `NewContainerdWorker` creates the base worker, registers an HTTP source using the daemon transport, and returns the wrapper. `Exporter` intercepts the Moby exporter name by resolving BuildKit's normal image exporter and wrapping it with Moby-specific callbacks and content labeling; all other exporters delegate to the base worker.

## State, Dependencies, and Risks
State is owned by the embedded BuildKit worker and content store. Risks include HTTP source registration failure only logging a warning, so HTTP source support can be absent at runtime. The Moby exporter path depends on wrapper correctness and content store label support. Tests are indirect.
