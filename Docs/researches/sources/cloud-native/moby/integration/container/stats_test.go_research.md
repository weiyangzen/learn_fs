# sources/cloud-native/moby/integration/container/stats_test.go

Purpose: Container stats API tests for one-shot/no-stream response shape and not-found errors.

Important APIs and flow: `TestStats` skips unsupported cgroup/memory environments, obtains daemon `Info`, runs a container, and calls `ContainerStats` with `Stream:false` and `IncludePreviousSample` true or false. It decodes exactly one `StatsResponse`, checks memory limit equals host `MemTotal`, checks whether `PreCPUStats` is zero or populated, and expects EOF on a second decode. `TestStatsContainerNotFound` verifies not-found errors for streaming and non-streaming stats calls.

State and dependencies: Uses cgroup memory accounting and a running container. It depends on stats JSON streaming behavior and host memory reporting.

Risks and signals: It guards client-visible stats response contracts, especially EOF behavior and previous CPU sample inclusion. Failures can break monitoring clients.
