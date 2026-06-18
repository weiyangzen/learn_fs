# sources/cloud-native/soci-snapshotter/benchmark/benchmarkTests.go

Purpose: benchmark workload functions comparing normal containerd overlayfs pulls/runs, SOCI lazy pulls/runs, and stargz lazy pulls/runs.

Important APIs/types/functions: `fatalf`, `PullImageFromRegistry`, `SociRPullPullImage`, `SociFullRun`, `OverlayFSFullRun`, `StargzFullRun`, `getContainerdProcess`, `getSociProcess`, and `getStargzProcess`.

Control flow: each benchmark starts isolated containerd and optional snapshotter processes, resets the benchmark timer around the measured flow, pulls images, creates containers/tasks, waits for a ready line, reports custom metrics (`pullDuration`, `unpackDuration`, `lazyTaskDuration`, `localTaskStats`), stops timers for cleanup, and tears down processes.

State and persistence: uses `/tmp` containerd/snapshotter roots, state dirs, and sockets; writes process logs under `./output`; deletes runtime state in process cleanup.

Dependencies/integration: depends on benchmark framework, containerd client, SOCI/stargz process starters elsewhere in benchmark package, image descriptors, and logrus/containerd logging.

Risks: closure use in callers must capture loop variables correctly. Benchmarks depend on external registries, host networking, root privileges, and ready-line correctness. Cleanup errors are mostly printed rather than fatal.

Test signals: Make benchmark targets and CI benchmark workflows produce result metrics.
