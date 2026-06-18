# sources/cloud-native/containerd/pkg/archive/compression/compression.go

## Purpose
Detects, compresses, and decompresses archive streams using uncompressed, gzip, and zstd formats, with optional external gzip decompressors.

## Important APIs, Types, And Functions
`Compression` enum includes `Uncompressed`, `Gzip`, `Zstd`, and `Unknown`. `DetectCompression`, `DecompressStream`, `CompressStream`, and `Extension` are public. Internals include pooled buffered readers, zstd skippable-frame detection, gzip external command detection, and `cmdStream`.

## Control Flow
Decompression peeks at the first 10 bytes, detects magic, then returns a wrapper around raw buffered input, gzip reader/external command pipe, or zstd reader. Compression returns an appropriate write closer. Gzip command detection prefers `igzip`, then `unpigz`, unless disabled by env vars.

## State And Persistence
Uses package-global `sync.Once` and `gzipPath` cache plus a `sync.Pool` of buffered readers. No persistent files are created.

## Dependencies And Integration Points
Uses Go gzip, klauspost zstd, external `igzip`/`unpigz`, containerd logging, and archive unpack/pull paths.

## Risks
Map iteration in `DetectCompression` is safe because magic values do not overlap, but order is not deterministic. `writeCloserWrapper.Close` ignores closer errors. External command stderr is surfaced only after read/pipe completion. Gzip path is detected once and cached despite later env/path changes.

## Test Signals
Fuzzer coverage calls `DecompressStream` on arbitrary bytes. Benchmarks cover performance and external gzip selection. Correctness tests may exist outside this subset.
