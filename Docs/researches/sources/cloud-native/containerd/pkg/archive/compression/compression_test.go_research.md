<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_test.go -->
# sources/cloud-native/containerd/pkg/archive/compression/compression_test.go

Purpose: test coverage for the archive compression package, especially gzip, optional pigz/unpigz integration, uncompressed pass-through behavior, command-backed streams, and zstd magic detection.

Important APIs and functions: `TestMain` forces gzip decompressor initialization before tests; `generateData`, `testCompress`, `testDecompress`, and `testCompressDecompress` are reusable helpers around `CompressStream`, `DecompressStream`, and `DetectCompression`. The test cases exercise `Compression` values `Gzip`, `Uncompressed`, and `Zstd`, plus internals `gzipPath`, `detectCommand`, `disablePigzEnv`, and `cmdStream`.

Control flow and state: tests generate a mixed random/zero/random byte buffer, compress it, assert compressed bytes are changed when appropriate, then read all decompressed output and compare with the original. Pigz tests temporarily mutate global `gzipPath` or fake `PATH`, and use `t.Setenv`/defers to restore state. `cmdStream` tests verify stdout forwarding and stderr-included error propagation.

Dependencies and integration: depends on the compression implementation in the same package, standard `compress/gzip`, `os/exec`, and platform PATH handling. It is an integration signal for external `unpigz`; if absent, the pigz path test is skipped.

Risks and test signals: randomness may hide pathological content but verifies large data paths. The fake PATH test guards environment disable handling. `TestDetectCompressionZstd` explicitly covers normal and skippable zstd frames, which is important for OCI artifacts that may contain leading skippable metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_test.go -->
