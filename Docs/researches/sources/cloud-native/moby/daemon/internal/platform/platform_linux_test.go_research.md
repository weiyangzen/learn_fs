<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go

Purpose: validates Linux possible-CPU range parsing.

Important APIs and types: `TestParsePossibleCPUs`.

Control flow: table-driven cases pass strings such as `0-3`, `0-2,4,6-7`, `5`, empty input, invalid tokens, and malformed ranges to `parsePossibleCPUs`.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: does not test reversed ranges or whitespace around segments.

Test signals: confirms primary supported `/sys` formats and nil-on-malformed behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux_test.go -->
