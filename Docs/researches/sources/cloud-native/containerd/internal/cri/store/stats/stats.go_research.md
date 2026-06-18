# Research: sources/cloud-native/containerd/internal/cri/store/stats/stats.go

This file defines `ContainerStats`, the minimal cached CPU sample used by CRI stores and stats conversion code. It contains `Timestamp`, the time at which stats were collected, and `UsageCoreNanoSeconds`, cumulative CPU usage across all cores since object creation.

The type is intentionally simple and has no methods, synchronization, persistence, or dependencies beyond Go `time`. It is embedded by pointer in `containerstore.Container.Stats` and `sandboxstore.Sandbox.Stats`, updated by Windows sandbox stats through `saveSandBoxMetrics`, and complemented by Linux `TimedStore` samples in `timed_store.go` and `StatsCollector`.

Its integration role is to provide the previous CPU cumulative sample required to compute instantaneous `UsageNanoCores`. Risks are semantic rather than structural: callers must keep timestamp and cumulative value from the same measurement, handle nil pointers for first sample/no data, and avoid using stale or reset cumulative counters without guard logic. Windows `getUsageNanoCores` currently does not check for decreasing cumulative values, while `TimedStore` does. Tests cover usage indirectly in Windows stats, container/sandbox store stats updates, and timed-store calculations.
