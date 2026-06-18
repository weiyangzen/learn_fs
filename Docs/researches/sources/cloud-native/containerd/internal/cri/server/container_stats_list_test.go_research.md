# sources/cloud-native/containerd/internal/cri/server/container_stats_list_test.go

## Purpose
This test file validates the shared stats conversion logic for CPU, memory, available bytes, working set, and partial list conversion behavior.

## Important APIs, Types, and Functions
Tests include `TestContainerMetricsCPUNanoCoreUsage`, `TestGetWorkingSet`, `TestGetWorkingSetV2`, `TestGetAvailableBytes`, `TestGetAvailableBytesV2`, `TestContainerMetricsMemory`, and `TestListContainerStats`. Helpers include `uint64Ptr` and `platformBasedMetricsData`.

## Control Flow, State, and Persistence
The tests use `newTestCRIService`, fake containers/sandboxes, synthetic cgroup v1/v2 and Windows metric payloads, and timestamp deltas. CPU nano-core tests verify first-sample nil, normal deltas, counter rollback, and store update behavior.

## Dependencies and Integration Points
It exercises cgroup stats structures, hcsshim stats on Windows, typeurl marshaling, platform defaults, container/sandbox stores, and CRI stats structures. It covers the platform-sensitive data consumed by `ContainerStats` and `ListContainerStats`.

## Risks and Test Signals
Signals are exact numerical expectations for memory working set, available bytes, RSS/page faults, and CPU rates. Test gaps include full task service RPC behavior, writable-layer snapshot accounting, and PSI conversion assertions.
