<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_handler.h -->
# sources/cloud-native/overlaybd/src/exporter_handler.h

Purpose: Prometheus text handler for OverlayBD metrics.

APIs and control flow: `ExposeMetrics::ExposeRender` stores tagged metric pointers for throughput, qps, latency, count, and cache values. `render` emits an alive gauge and each registered metric in Prometheus text format. `handle_request` returns HTTP 200 with content type `text/plain; version=0.0.4`.

State and persistence: Metrics live in memory and are sampled from Photon counters; no persisted state.

Dependencies and integration: Used by `OverlayBDMetric` and `ExporterServer` when exporter config is enabled.

Risks and test signals: Metric name typo `Throughtput` is externally visible. Tests should GET `/metrics` and verify alive plus read/download counters after IO.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_handler.h -->
