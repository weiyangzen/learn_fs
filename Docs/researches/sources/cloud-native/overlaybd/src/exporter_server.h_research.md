<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_server.h -->
# sources/cloud-native/overlaybd/src/exporter_server.h

Purpose: HTTP server wrapper and metric registry for Prometheus export.

APIs and types: `OverlayBDMetric` owns `MetricMeta pread` and `download`, then registers them with `ExposeRender`. `ExporterServer` binds a Photon TCP socket on configured port, creates an HTTP server, installs the metrics handler under `uriPrefix`, starts the loop, and marks `ready`.

State and persistence: Holds live socket and HTTP server pointers; all state is in memory.

Dependencies and integration: `ImageService::init` wraps registry/cache filesystems with `MetricFS` and starts this server when enabled.

Risks and test signals: Bind failures abort image service initialization. Validation is startup with exporter enabled and HTTP scrape response.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/exporter_server.h -->
