<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go

Purpose: validates rolling checksum invariants and benchmarks split scanning.

Important APIs/types/functions: `TestSum` and `BenchmarkRollsum`.

Control flow: `TestSum` fills a deterministic random buffer, compares checksum results for windows that should be equivalent after roll-in/roll-out behavior, then walks 500 positions comparing incrementally rolled digest with freshly computed digest. The benchmark scans a 5 MiB buffer, calls `Roll`, checks `OnSplit`, and logs split frequency.

State/persistence: in-memory random buffers only.

Dependencies/integration: exercises `NewRollSum`, `Roll`, `Digest`, `OnSplit`, and `Bits`.

Risks/test signal: guards the checksum ring-buffer math. Benchmark output is informational and does not enforce chunk-size distribution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go -->
