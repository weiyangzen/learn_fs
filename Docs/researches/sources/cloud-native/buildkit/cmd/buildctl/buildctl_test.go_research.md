# Research: sources/cloud-native/buildkit/cmd/buildctl/buildctl_test.go

Purpose: is the top-level integration test harness for the `buildctl` binary plus a focused unit test for metadata file serialization. It initializes OCI and containerd workers so the integration suite can exercise multiple daemon backends.

Important APIs and flow: `init` registers worker fixtures. `TestCLIIntegration` delegates to `integration.Run` with disk usage, build, prune, and usage tests and mirrors official images. `testUsage` verifies the base command and help path succeed. `TestWriteMetadataFile` feeds exporter responses through `writeMetadataFile`, including ordinary strings, base64 JSON objects, empty objects, non-object JSON, invalid semantic JSON for this purpose, and null-containing objects.

State and dependencies: test state is temporary directories plus integration daemon/containerd state. The metadata test verifies local atomic file output and JSON unmarshaling behavior without daemon dependencies.

Risks and test signals: this file gives good regression signals for CLI wiring and metadata conversion, especially the intentionally narrow rule that only non-empty JSON objects are embedded as raw JSON. It does not validate trace/cache metric output or every command in the CLI tree.
