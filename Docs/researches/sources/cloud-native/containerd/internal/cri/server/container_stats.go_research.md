# sources/cloud-native/containerd/internal/cri/server/container_stats.go

## Purpose
This file implements CRI `ContainerStats` for one container. It fetches task metrics by container ID and converts the single result into CRI stats.

## Important APIs, Types, and Functions
`(*criService).ContainerStats` uses `containerStore.Get`, containerd `TaskService().Metrics`, `tasks.MetricsRequest`, `getMetricsHandler`, and the platform-specific metrics decoder returned by `container_stats_list.go`.

## Control Flow, State, and Persistence
The method resolves the canonical container ID, requests exactly one metric with filter `id==<id>`, rejects responses that do not contain exactly one metric, obtains a handler based on sandbox platform/runtime, decodes metrics, and returns `runtime.ContainerStatsResponse`. It may update CPU usage history through shared stats conversion helpers.

## Dependencies and Integration Points
It integrates single-container CRI stats with the same Linux/Windows conversion pipeline used by list stats, snapshot writable-layer accounting, sandbox platform detection, and containerd task metrics.

## Risks and Test Signals
Risks include metrics response cardinality mismatch, unsupported sandbox platforms, missing task metrics for stopped containers, and conversion errors. Direct tests are in `container_stats_list_test.go` for shared helpers rather than this thin RPC wrapper.
