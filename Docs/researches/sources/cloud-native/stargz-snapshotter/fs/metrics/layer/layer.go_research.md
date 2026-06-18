## sources/cloud-native/stargz-snapshotter/fs/metrics/layer/layer.go

Purpose: declares per-mounted-layer metric definitions for fetched size, prefetched size, and total layer size.

Important APIs/types/functions: package variable `layerMetrics` is a slice of `metric` definitions consumed by the layer metrics controller. Each metric defines name, help text, unit `metrics.Bytes`, Prometheus value type `CounterValue`, and a `getValues` function that reads `layer.Layer.Info()`.

Control flow: no active control flow in this file; `Controller.Collect` in `metrics.go` iterates these definitions and emits values for each registered mountpoint/layer.

State and persistence: metric definitions are immutable package-level state. Actual layer references live in the controller.

Dependencies and integration points: depends on `fs/layer.Layer`, docker/go-metrics units, and Prometheus value types. Integrated by `NewLayerMetrics`, which appends this slice to a controller.

Risks: values like fetched size and prefetched size can change over time but are emitted as `CounterValue`; if they ever decrease due to cache eviction/reconnect semantics, Prometheus counter semantics would be wrong. Calling `Info()` once per metric can repeat work and potentially observe slightly different snapshots across metrics.

Test signals: no direct tests. Metrics are operational observability only in this subset.
