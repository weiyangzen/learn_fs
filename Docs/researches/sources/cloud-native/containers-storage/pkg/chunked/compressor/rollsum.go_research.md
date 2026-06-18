<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go

Purpose: rolling checksum implementation used for content-defined chunk splitting in zstd:chunked compression.

Important APIs/types/functions: constants `windowSize`, `charOffset`, `blobBits`, `blobSize`; type `RollSum`; functions `NewRollSum`, `add`, `Roll`, `OnSplit`, `OnSplitWithBits`, `Bits`, and `Digest`.

Control flow: `NewRollSum` initializes sums as if the 64-byte window were filled with offset bytes. `Roll` replaces the next ring-buffer byte, updates `s1` and `s2`, and advances the window offset. `OnSplit` and `OnSplitWithBits` test low checksum bits for split boundaries. `Bits` estimates split strength from trailing zeros in the inverted digest-derived value. `Digest` combines `s1` and low `s2`.

State/persistence: in-memory rolling window and sums only.

Dependencies/integration: used by `rollingChecksumReader` in `compressor.go` to decide chunk boundaries; derived from Perkeep/bup-style rolling checksum code.

Risks: split distribution directly affects chunk sizes, deduplication, and compression seekability. `windowSize` must remain a power of two because ring advancement uses bit masking.

Test signals: `rollsum_test.go` verifies rolling digest invariance across shifted windows and includes a benchmark.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go -->
