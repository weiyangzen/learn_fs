# sources/cloud-native/nydus/smoke/tests/tool/container.go

## Purpose
This helper centralizes container workload recipes and metrics collection for Nydus snapshotter smoke/performance tests.

## Important APIs, Types, And Functions
`ContainerMetrics` stores E2E time, conversion time, backend reads, and image size. `RunArgs` describes readiness URL, command args, optional bind mount, and baseline metric maps. `urlWait` contains long-running HTTP workloads such as `wordpress` and `node`; `cmdStdout` contains one-shot language runtime workloads. `SupportContainerImage` and `GetRunArgs` query recipes. `runURLWaitContainer` starts `nerdctl run -d --net=host` and polls `WaitURL`. `runCmdStdoutContainer` runs an interactive command script. `RunContainerWithBaseline` runs Nydus and enforces read baselines. `RunContainer` returns runtime metrics. `RunContainerSimple` starts a workload with optional cleanup. `ClearContainer` removes the container and image. `getContainerBackendMetrics` connects to a discovered nydusd API socket and decodes backend metrics. `searchAPISockPath` finds the first daemon socket directory under the snapshotter socket root.

## Control Flow
Recipes are selected by image repo name stripped from the full reference. Workload launch either waits for an HTTP endpoint or waits for command completion. For Nydus snapshotter runs, metrics are fetched from the daemon API socket after workload launch.

## State And Persistence
The helper creates/removes containers and images through `nerdctl`. It may mount repository texture directories into containers. Metrics are read from live daemon state and not persisted by this helper.

## Dependencies And Integration Points
It requires `sudo nerdctl`, containerd, Nydus snapshotter, host networking, HTTP readiness, and Nydus daemon API socket layout under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus/socket`.

## Risks
Host-network port 80 can conflict across parallel tests. `searchAPISockPath` picks the first directory and may choose the wrong daemon if multiple instances exist. ClearContainer removes images as well as containers, which can affect shared image cache. Baselines are environment-sensitive.

## Test Signals
Signals include successful workload readiness/completion, backend metrics availability, and read-count/read-byte comparisons against baselines.
