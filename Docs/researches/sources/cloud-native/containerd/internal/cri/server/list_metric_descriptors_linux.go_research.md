
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go -->
# sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go

## Purpose

This Linux-specific file implements CRI `ListMetricDescriptors`, returning the static descriptor set supported by Linux pod sandbox metrics collection.

## Important APIs, Types, and Functions

The public handler is `(*criService).ListMetricDescriptors`. The helper `(*criService).getMetricDescriptors` returns a map from category constants to descriptor slices.

## Control Flow

The handler gets the descriptor map, appends all category slices into one flat slice, and returns it in `runtime.ListMetricDescriptorsResponse`. The category map includes CPU, memory, network, disk usage, disk IO, process, miscellaneous, and container spec descriptors.

## State and Persistence Behavior

The handler is read-only and returns pointers to package-level descriptor objects. It does not collect metric values or mutate CRI/containerd state.

## Dependencies and Integration Points

Dependencies include context and CRI runtime API. It integrates with the Linux `ListPodSandboxMetrics` implementation and with kubelet or metrics consumers that first discover descriptors.

## Risks and Edge Cases

Map iteration order is not deterministic, so descriptor response order can vary. Returning shared descriptor pointers means caller-side mutation would be unsafe if not treated as read-only. Non-Linux platforms intentionally use a different unimplemented handler.

## Test Signals

Useful tests would assert that every emitted Linux metric has a descriptor, that descriptor names are unique, that all expected categories are present, and that order-insensitive clients handle the response.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/list_metric_descriptors_linux.go -->
