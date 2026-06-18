<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_test.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_test.go

Purpose: tests spec-file plugin discovery. It creates temp `.spec` and `.json` plugin definitions, invokes a `LocalRegistry`, and asserts plugin address/TLS config behavior including insecure defaults when CA is omitted. State is temporary spec files. Dependencies are os/path testing helpers. Risks covered include file parsing and JSON defaults; Unix socket scanning is covered separately. Test signal is focused on cross-platform spec discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_test.go -->
