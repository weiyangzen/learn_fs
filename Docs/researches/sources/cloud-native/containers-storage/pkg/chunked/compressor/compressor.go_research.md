<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go

Purpose: implements zstd:chunked tar stream creation with per-file/per-chunk offsets, digests, hole detection, rolling checksums, tar-split metadata, and final manifest frames.

Important APIs/types/functions: constants `RollsumBits` and `holesThreshold`; `holesFinder`; `rollingChecksumReader`; `chunk`; `tarSplitData`; `newTarSplitData`; `writeZstdChunkedStream`; `zstdChunkedWriter`; `makeZstdChunkedWriter`; `ZstdCompressor`; `noCompression`; `NoCompression`.

Control flow: `makeZstdChunkedWriter` returns a pipe-backed writer and runs `writeZstdChunkedStream` in a goroutine. The stream writer wraps the tar input with tar-split packer, writes raw tar headers, restarts zstd at file payload boundaries and content-defined chunk boundaries, tracks chunk compressed offsets, computes payload and chunk digests, treats long zero runs as hole chunks, builds `minimal.FileMetadata` entries, appends remaining tar bytes, closes zstd writers, packages compressed tar-split data, and calls `minimal.WriteZstdChunkedManifest`. `ZstdCompressor` defaults level 10. `NoCompression` uses a resettable writer shim for internal conversion paths.

State/persistence: writes compressed output and metadata annotations to caller-provided writer/metadata map. Maintains in-memory tar-split compressed bytes and metadata slice.

Dependencies/integration: intentionally avoids graphdriver dependencies because containers/image imports it. Uses minimal chunked metadata, `ioutils.WriteCounter`, OCI digests, tar-split, zstd writer factory, and `RollSum`.

Risks: streaming/goroutine errors must propagate through pipe reads/writes; incorrect restart offsets or chunk digests break random access. `holesFinder` and rolling checksum boundaries affect dedup efficiency and sparse-zero representation. `NoCompression` output is intentionally not generally zstd:chunked compliant.

Test signals: `compressor_test.go` covers hole detection and no-compression writer behavior; rollsum tests validate checksum invariants. Broader chunked tests outside this subset verify generated manifest parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go -->
