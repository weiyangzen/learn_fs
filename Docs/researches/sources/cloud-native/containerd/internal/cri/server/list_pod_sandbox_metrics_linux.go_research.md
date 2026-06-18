
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go

## Purpose

This Linux-specific file implements CRI `ListPodSandboxMetrics`. It collects pod-level network metrics and container-level CPU, memory, disk IO, filesystem, process, ulimit, and spec resource metrics from containerd tasks, cgroup v1/v2 stats, rootfs usage, and `/proc`.

## Important APIs, Types, and Functions

Key functions are `(*criService).ListPodSandboxMetrics`, `collectPodSandboxMetrics`, `collectContainerMetrics`, `extractCPUMetrics`, `extractMemoryMetrics`, `extractDiskIOMetrics`, `extractProcessMetrics`, `extractContainerSpecMetrics`, `findContainerTaskRootfs`, `extractFilesystemMetrics`, and `getContainerProcessDescriptorCount`. A package-level rate limiter and errgroup concurrency limit both cap concurrent collection at ten.

## Control Flow

The handler applies the containerd namespace to context, precomputes a sandbox-to-containers map from the container store, then iterates ready sandboxes. For each ready sandbox it waits on a rate limiter and starts an errgroup task. The task builds base pod labels, collects sandbox network metrics from the sandbox network namespace when present, then collects each associated container's metrics. Transient unavailable/not-found errors are logged and skipped; cancellation stops collection; other per-object errors are logged while returning partial results.

Container metrics load the container task, call `task.Metrics`, unmarshal cgroup v1 or v2 stats with `typeurl`, build label values, add last-seen and start-time metrics, then independently append CPU, memory, disk IO, filesystem, process, and spec metrics. Each extractor logs and allows partial metric output if it fails.

CPU and memory extraction normalize cgroup v1 nanoseconds and cgroup v2 microseconds into seconds-like counters, and map cgroup-specific fields into descriptor names. Disk IO maps blkio or cgroup v2 IO stats into read/write counters. Process metrics include pids, thread limits, ulimit soft values, and `/proc/<pid>/fd` descriptor/socket counts. Filesystem metrics infer the task rootfs path from containerd state layout, stat the filesystem, and prefer snapshotter usage when available.

## State and Persistence Behavior

The implementation is read-only over CRI stores, containerd tasks, cgroup metrics, snapshot usage, rootfs stats, and `/proc`. It returns a snapshot of metrics and does not persist counters. It logs partial failures but still returns collected metrics.

## Dependencies and Integration Points

Dependencies include cgroup v1/v2 stats, containerd task APIs, CRI stores, sandbox store, snapshot service, network namespace stats helper `getContainerNetIO`, CRI descriptor variables, NRI name for bundle path construction, errgroup, rate limiter, and Linux `/proc`/`statfs`. It integrates with `ListMetricDescriptors` via shared descriptor names and label order.

## Risks and Edge Cases

The rootfs finder is explicitly described as inherently broken because task specs use relative root paths; it reconstructs a containerd bundle path from state dir, runtime plugin, namespace/name, and container ID. Filesystem device labels are acknowledged as wrong. Start time uses `StartedAt` nanoseconds as a gauge named seconds, which may need scrutiny. Cgroup v1/v2 field semantics differ, and some v2 values are zero-filled for unavailable v1-style counters. Returning partial results can mask systemic collection failures.

## Test Signals

Useful tests should cover ready-sandbox filtering, partial-result behavior, cgroup v1 and v2 CPU/memory/IO mappings, network namespace metrics, process fd/socket counting, ulimit extraction, spec metric extraction, rootfs inference failures, snapshot usage fallback, descriptor coverage, rate limiting, and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_pod_sandbox_metrics_linux.go -->
