# Research: sources/cloud-native/containerd/internal/cri/store/stats/timed_store_test.go

This test file validates `TimedStore` behavior. Basic tests confirm a new store is empty, `GetLatest` returns nil, and `GetLatestUsageNanoCores` reports false until at least two samples exist. Add/get tests verify the first sample stores cumulative CPU but has zero calculated nanocores.

Rate tests check one-core and half-core calculations from cumulative CPU deltas over one- and two-second intervals. Capacity tests verify `maxItems` retains only newest samples, and age eviction keeps samples strictly after the eviction time. `TestTimedStoreConcurrentAccess` runs multiple writer and reader goroutines and asserts no panic plus bounded size. `TestCalculateUsageNanoCores` covers normal one-core/two-core calculations, zero time delta, negative time delta, and CPU usage decreasing after restart.

The test signal is strong for math and in-memory concurrency but does not cover out-of-order insertion explicitly, no-limit max item behavior beyond age eviction, float precision at very large counters, or integration with Linux `StatsCollector`. It guards the core correctness of `UsageNanoCores` values used by CRI stats responses.
