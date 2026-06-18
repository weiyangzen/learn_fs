## sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked_test.go

Purpose: validates the zstd:chunked compression implementation through the shared eStargz compression suite and direct footer round-trip tests.

Important APIs and helpers: `TestZstdChunked` runs `estargz.CompressionTestSuite` with zstd levels `SpeedFastest`, `SpeedDefault`, and `SpeedBetterCompression`. `zstdController` combines `Compressor` and `Decompressor`, implements stream validation with `TestStreams`, and computes DiffID by zstd-decompressing the blob into sha256. `TestZstdChunkedFooter` iterates offsets and compressed/raw sizes through `zstdFooterBytes` and `Decompressor.ParseFooter`. `nextIndex` is a local frame scanning helper.

Control flow: shared suite builds and opens archives, checks TOC/chunk/digest behavior, and expects stream offsets. `TestStreams` sorts expected offsets, adjusts the final footer offset by the 8-byte skippable frame header, scans the blob for zstd or skippable frame magic, and fails if expected frame starts are absent. Footer tests assert payload size equals `off - 8`, TOC offset equals `off`, and parsed TOC size equals compressed size.

State and persistence: all test data is in memory. No metadata annotation assertions are present even though the compressor can populate annotations.

Dependencies and integration points: uses `klauspost/compress/zstd`, shared `estargz` test utilities, and package-local frame magic constants. It indirectly verifies compatibility with `estargz.Build`, `Open`, and verification logic for zstd-chunked codecs.

Risks: `SpeedBestCompression` is intentionally skipped for CI memory reasons, leaving highest compression level less covered. Frame scanning is heuristic and looks for magic sequences rather than parsing complete zstd frame headers. Tests do not cover malformed short footers, invalid footer magic beyond direct parser error path, metadata annotation values, or TOC copy failure behavior.

Test signals: strong normal-operation signal for zstd-chunked archives and footer encoding; moderate signal for stream layout because magic scanning can be fooled by magic-like bytes in payloads, though suite fixtures make that unlikely.
