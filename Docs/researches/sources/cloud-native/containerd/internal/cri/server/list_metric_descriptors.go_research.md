
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go

## Purpose

This file declares the CRI metric descriptor constants and descriptor objects used by `ListMetricDescriptors` and by the Linux pod sandbox metrics collector. It defines the names, help text, and label keys for CPU, memory, network, disk, disk IO, process, miscellaneous, and container spec metrics.

## Important APIs, Types, and Functions

It exports category constants such as `CPUUsageMetrics`, `MemoryUsageMetrics`, `NetworkUsageMetrics`, `DiskIOMetrics`, `DiskUsageMetrics`, `ProcessMetrics`, `MiscellaneousMetrics`, and `ContainerSpecMetrics`. It declares label key slices `baseLabelKeys`, `networkLabelKeys`, and `diskLabelKeys`, plus many `*runtime.MetricDescriptor` variables such as `containerCPUUsageSecondsTotal`, `containerMemoryUsageBytes`, `containerNetworkReceiveBytesTotal`, `containerFsUsageBytes`, `containerProcesses`, and `containerSpecMemoryLimitBytes`.

## Control Flow

There is no executable control flow beyond package initialization of variables. Descriptor arrays with extra labels are built with `append` over copies or base slices for dimensions such as network interface, disk device, failure type, scope, major/minor/operation, and ulimit.

## State and Persistence Behavior

Descriptors are process-global immutable-by-convention pointers. The file stores no metrics values and performs no persistence.

## Dependencies and Integration Points

The file depends on CRI runtime API types. Linux descriptor listing groups these variables in `getMetricDescriptors`, and Linux metric extraction functions use descriptor names and label order when building `runtime.Metric` values.

## Risks and Edge Cases

Because descriptors are mutable pointer values, accidental mutation could affect all responses and emitted metrics. Label order must stay aligned with `ListPodSandboxMetrics` extraction code. The help text and metric names should remain compatible with consumers expecting cAdvisor-like metrics.

## Test Signals

Useful tests would verify descriptor name uniqueness, expected label key order, descriptor categories matching emitted metric names, and no accidental mutation between calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors.go -->
