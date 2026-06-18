<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/metrics_fs.h -->
# sources/cloud-native/overlaybd/src/metrics_fs.h

Purpose: Filesystem and file wrappers that record read metrics.

APIs and types: `MetricMeta` groups latency, throughput, qps, total, and interval counters. `MetricFile` wraps `pread`, `preadv`, and `preadv2`, incrementing qps, latency, throughput, and total on positive reads. `MetricFS` wraps `open` calls to return `MetricFile`.

State and persistence: Metrics are in-memory Photon counters.

Dependencies and integration: `ImageService` wraps underlay registryfs for download metrics and cached fs for pread metrics when exporter is enabled.

Risks and test signals: Only read paths are tracked, and interval counter is not rendered by current exporter. Tests should assert counter changes after remote and cached reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/metrics_fs.h -->
