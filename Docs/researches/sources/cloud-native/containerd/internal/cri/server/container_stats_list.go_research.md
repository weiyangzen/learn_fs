# sources/cloud-native/containerd/internal/cri/server/container_stats_list.go

## Purpose
This file implements CRI `ListContainerStats` and the core conversion of containerd task metrics into CRI CPU, memory, IO, PID, and writable-layer stats for Linux and Windows containers.

## Important APIs, Types, and Functions
Key functions/types are `ListContainerStats`, `listContainerStats`, `containerStats`, `metricsHandler`, `getMetricsHandler`, `toContainerStats`, `toCRIContainerStats`, `getUsageNanoCores`, `normalizeContainerStatsFilter`, `buildTaskMetricsRequest`, `matchLabelSelector`, `windowsContainerMetrics`, `linuxContainerMetrics`, `getWorkingSet`, `getWorkingSetV2`, `getAvailableBytes`, `getAvailableBytesV2`, `convertCg2PSIToCRI`, `cpuContainerStats`, `memoryContainerStats`, and `ioContainerStats`.

## Control Flow, State, and Persistence
The list path builds a metrics request from filters, calls containerd task metrics, maps metrics by ID, obtains/caches a metrics handler per sandbox, decodes platform metrics, calculates instantaneous CPU nano cores, and returns CRI stats. CPU rate state persists in the background stats collector when available or in container/sandbox store `Stats` history as a fallback. Snapshot store data supplies writable-layer bytes and inodes.

## Dependencies and Integration Points
Dependencies include cgroup v1/v2 stats, hcsshim Windows stats, containerd task metrics API, typeurl protobuf unpacking, sandbox platform service, runtime snapshotter selection, image filesystem paths, snapshot store, and CRI stats models.

## Risks and Test Signals
Risks include wrong cgroup v1/v2 type handling, rate calculation on first sample or counter rollback, unsupported platforms, nil metrics, missing snapshots, and PSI unit conversion. Tests cover CPU nano-core deltas, working set/available-byte math, memory conversion, platform metrics data, and skipped containers when stores are incomplete.
