# sources/cloud-native/nydus/contrib/nydusify/pkg/metrics/fileexporter/fileexporter_test.go

Purpose: verifies that the file exporter writes Prometheus metrics to disk.

Important APIs under test: `New` and `FileExporter.Export`.

Control flow and state: the test creates a fresh Prometheus registry, registers and increments a counter, installs it into `metrics.Registry`, exports to a temporary file, reads the file back, and asserts that the counter name is present.

Dependencies and integration points: Prometheus registry/counter APIs, the global metrics registry, temporary filesystem output, and testify require.

Risks and test signals: the test validates the happy path only. It does not cover unwritable paths or nil registry behavior, matching the implementation's error-ignoring behavior.
