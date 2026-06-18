# sources/cloud-native/soci-snapshotter/fs/metrics/layer/layer.go

Purpose: declares the per-layer metrics exposed by the layer metrics controller.

Important APIs and flow: `layerMetrics` contains two `metric` definitions: `layer_fetched_size`, which reports `l.Info().FetchedSize`, and `layer_size`, which reports `l.Info().Size`. Both use byte units and `prometheus.CounterValue`, and both rely on the controller to add digest and mountpoint labels.

State and persistence: no mutable state in this file. Metric values are read from live `layer.Layer` instances at scrape time.

Dependencies and integration: depends on the layer interface, Docker go-metrics units, and Prometheus value types. `metrics.go` appends this list into a `Controller` registered in a Docker metrics namespace by `fs.NewFilesystem`.

Risks and test signals: `CounterValue` for fetched size can be problematic if a layer object is replaced or fetched-size reporting decreases, because Prometheus counters should be monotonic. No tests directly validate descriptor names, units, or scrape values.
