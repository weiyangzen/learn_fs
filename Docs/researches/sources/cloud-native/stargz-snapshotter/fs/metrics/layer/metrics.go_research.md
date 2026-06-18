## sources/cloud-native/stargz-snapshotter/fs/metrics/layer/metrics.go

Purpose: implements a docker/go-metrics collector/controller that tracks active mounted layers by mountpoint and exports the metric definitions from `layer.go`.

Important APIs/types/functions: `NewLayerMetrics` creates a `Controller`, attaches layer metric definitions, adds it to a metrics namespace, and returns a no-op controller when namespace is nil. `Controller` implements `Describe` and `Collect`. `Add` and `Remove` register/unregister mountpoint-to-layer mappings. `metric.desc` creates descriptors with labels `digest`, `mountpoint`, and optional metric-specific labels. `metric.collect` emits `prometheus.MustNewConstMetric`.

Control flow: filesystem mount calls `Add`; unmount calls `Remove`. During collection, the controller R-locks the layer map, starts a goroutine per mounted layer using `sync.WaitGroup.Go`, collects each metric for that layer, unlocks, and waits. Each metric reads layer info and sends a Prometheus metric to the channel.

State and persistence: `Controller.layer` stores active layers keyed by mountpoint under `layerMu`. Namespace and metric definitions persist for controller lifetime. No disk persistence.

Dependencies and integration points: used from `fs.NewFilesystem`, `fs.Mount`, and `fs.Unmount`. Depends on docker/go-metrics namespace descriptors, Prometheus collector interfaces, and the `layer.Layer` info contract.

Risks: `sync.WaitGroup.Go` requires a Go version that provides that method; older Go toolchains would fail to build. `Collect` holds the read lock while spawning and waiting for all goroutines, so `Add`/`Remove` block until collection finishes. Concurrent metric collection calls `l.Info()` from multiple goroutines, so layer implementations must remain concurrency-safe. A nil namespace intentionally disables all operations.

Test signals: no direct tests. Indirect runtime coverage comes from filesystem mounting registering/removing layers, but metric output correctness is not asserted here.
