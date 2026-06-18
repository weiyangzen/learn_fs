# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/data/labels.go

This file contains shared label-name constants for metrics declared in `pkg/metrics/data`. Labels include image reference, nydusd event, version, daemon ID, snapshot operation, and credential result.

There is no runtime control flow or persistence. The constants are a small but important compatibility surface because metric vectors across auth, cache, daemon, filesystem, and snapshotter data use them. Renaming any value changes the exported Prometheus label schema.

Integration points are all metric declarations and collectors. Risks include label cardinality, especially `image_ref` and `daemon_id`, and inconsistent result values for credential metrics because only the label name is centralized. There are no direct tests for this file; registration failures would appear through metrics registry initialization if label descriptors became inconsistent.
