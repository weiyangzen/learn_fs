# sources/cloud-native/cri-o/server/metric_descriptors_list.go

Purpose: implements CRI `ListMetricDescriptors` by projecting configured pod metric descriptors.

Important APIs and functions: `ListMetricDescriptors` calls `s.config.EnabledPodMetrics()`, then `s.PopulateMetricDescriptors`, flattens the returned map values, and returns `types.ListMetricDescriptorsResponse`.

Control flow: counts total descriptors for capacity, appends all descriptor slices without sorting, and returns them.

State and persistence: read-only over server config and descriptor generation.

Dependencies and integration: integrates Kubernetes CRI runtime metric descriptors with CRI-O's internal metric descriptor population helpers.

Risks: response order follows map iteration for descriptor groups, so callers should not depend on deterministic ordering unless `PopulateMetricDescriptors` returns stable map behavior elsewhere.

Test signals: no direct tests in this subset.
