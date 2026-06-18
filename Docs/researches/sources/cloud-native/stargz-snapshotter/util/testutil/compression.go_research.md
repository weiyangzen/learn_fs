<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/compression.go -->
# sources/cloud-native/stargz-snapshotter/util/testutil/compression.go

## Purpose
Defines compression factories used by tests to create gzip, zstd chunked, and external-TOC eStargz compressors/decompressors behind a common interface.

## Important APIs, Types, And Functions
- `Compression` combines estargz compressor/decompressor behavior with `DecompressTOC`.
- `CompressionFactory` returns a fresh `Compression`.
- `ZstdCompressionWithLevel`, `GzipCompressionWithLevel`, and `ExternalTOCGzipCompressionWithLevel` construct configured factories.
- External TOC compression wires a decompressor that reads TOC bytes from the matching compressor.

## Control Flow
Factory calls create compressor/decompressor pairs. External TOC factory captures the compressor in a closure so TOC reads reflect the generated external TOC data.

## State And Persistence
Compression state is per factory invocation. No files are written.

## Dependencies And Integration Points
Used by tests around estargz metadata and blob generation. Depends on estargz, external TOC, zstdchunked, and klauspost zstd.

## Risks And Edge Cases
External TOC decompressor is tied to the compressor instance, so reusing it across unrelated blobs would be invalid. Compression level validity is delegated to underlying libraries.

## Test Signals
Signals include round-trip compression/decompression, TOC decompression success, and expected behavior at chosen compression levels.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/testutil/compression.go -->
