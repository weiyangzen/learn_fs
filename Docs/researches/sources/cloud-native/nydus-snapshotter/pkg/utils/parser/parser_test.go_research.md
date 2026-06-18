<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go

Purpose: verifies successful memory configuration parsing for supported formats.

Important test: `TestMemoryLimitToBytes` table-drives `MemoryConfigToBytes` with `totalMemoryBytes=10000`. It checks empty string, whole and fractional percentages, raw byte values, explicit `B`, and IEC units from Ki through Pi with and without trailing `B`.

Control flow and state: tests rely on the package singleton unit map being lazily initialized through the production function.

Dependencies/integration: uses testify assertions.

Risks and test signals: this test is a positive-case regression suite. It does not cover malformed input, unknown units, lowercase units, overflow/truncation of large floats, or regexp partial matches. Because production returns zero for unknown units, adding negative tests would likely reveal a validation gap.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/parser/parser_test.go -->
