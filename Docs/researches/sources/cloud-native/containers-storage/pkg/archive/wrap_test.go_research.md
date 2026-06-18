<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/wrap_test.go

Purpose: tests `Generate` tar helper output.

Important APIs/types/functions: `TestGenerateEmptyFile` and `TestGenerateWithContent`.

Control flow: each test calls `Generate`, reads the returned tar stream with `tar.NewReader`, collects header names and payload strings, and compares them with expected pairs.

State/persistence: in-memory buffers only.

Dependencies/integration: verifies the helper produces a valid tar stream consumable by Go's tar reader.

Risks/test signal: coverage is intentionally narrow; it does not inspect permissions, multiple pairs, malformed names, or large payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap_test.go -->
