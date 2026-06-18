# sources/cloud-native/cri-o/server/sandbox_metrics_list.go

Purpose: implements CRI pod sandbox metrics listing and streaming.

Important APIs and functions: `ListPodSandboxMetrics`, `StreamPodSandboxMetrics`, and `listPodSandboxMetrics`.

Control flow: fetches all sandboxes, converts them through `MetricsForPodSandboxList`, then appends metrics with a non-nil `GetMetric()` into the response. Streaming chunks by `streamChunkSize`.

State and persistence: read-only over sandbox store and metrics providers.

Dependencies and integration: CRI pod sandbox/container metrics APIs and CRI-O metrics projection helpers.

Risks: the `else` branch dereferences `metrics.GetMetric()` after checking that it is nil, which appears unreachable without panic if executed. The function also ignores request filters because `ListPodSandboxMetricsRequest` carries no filter in this implementation.

Test signals: no direct tests in this subset.
