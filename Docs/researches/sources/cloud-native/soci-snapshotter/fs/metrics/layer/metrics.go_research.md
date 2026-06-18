# sources/cloud-native/soci-snapshotter/fs/metrics/layer/metrics.go

Purpose: implements a Prometheus collector/controller that tracks mounted layers and emits per-layer metrics with digest and mountpoint labels.

Important APIs and flow: `NewLayerMetrics` returns a no-op controller when the namespace is nil; otherwise it initializes maps, appends `layerMetrics`, and adds itself to the Docker metrics namespace. `Describe` emits descriptors for each metric. `Collect` takes a read lock, starts a goroutine per registered layer, and each goroutine emits all metric values for that mountpoint. `Add` and `Remove` mutate the mountpoint-to-layer map under lock and no-op when metrics are disabled. `metric.desc` builds descriptors and `metric.collect` calls `prometheus.MustNewConstMetric`.

State and persistence: in-memory map of mountpoint keys to live `layer.Layer` references protected by an RW mutex. No persistent state.

Dependencies and integration: `fs.Mount` registers layers, `fs.Unmount` removes them, and Docker go-metrics namespace exposes the controller to Prometheus. It calls `Layer.Info` during collection.

Risks and test signals: `Collect` holds the read lock while launching and waiting for goroutines, so `Add`/`Remove` block until the scrape completes. The closure uses loop variables in a goroutine; in modern Go this is safe for range variables, but older language versions would have been risky. No tests cover concurrent add/remove/scrape or no-op mode.
