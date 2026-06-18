<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix_test.go -->
# sources/cloud-native/moby/daemon/info_unix_test.go

Purpose: Unix-only parser tests for extracting version and commit details from init and OCI runtime command output.

Important APIs and control flow: `TestParseInitVersion` checks `tini version` forms with optional git commits and invalid strings. `TestParseRuntimeVersion` checks runc and crun style outputs, commit-only output, and invalid strings.

State and persistence: no state; table-driven pure parser tests.

Dependencies and integration: uses `gotest.tools` assertions and is guarded by `!windows`. It protects helpers used by `fillPlatformInfo` and `fillPlatformVersion`.

Risks: tests cover known output formats, not every runtime implementation. Assertions accept any error text for invalid cases, so exact diagnostics can change.

Test signals: direct coverage for version parsing edge cases that feed system API component details.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix_test.go -->
