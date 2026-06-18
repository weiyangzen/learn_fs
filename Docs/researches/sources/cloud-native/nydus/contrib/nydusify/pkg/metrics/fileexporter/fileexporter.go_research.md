# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter.go

Purpose: provides a simple metrics exporter that writes the current nydusify Prometheus registry to a textfile.

Important APIs/types/functions: `FileExporter`, `New`, and `Export`.

Control flow: `New` records the target file name. `Export` calls `prometheus.WriteToTextfile` with that name and the package-global `metrics.Registry`.

State and persistence: output is persisted to the filesystem path supplied to `New`. The exporter does not hold metric state itself; it depends on the global registry from `pkg/metrics`.

Dependencies and integration points: Prometheus client_golang textfile export and nydusify metrics registration.

Risks and test signals: `Export` ignores the returned error from `WriteToTextfile`, so callers cannot detect unwritable paths or nil registry failures. There is no locking around registry access beyond Prometheus internals.
