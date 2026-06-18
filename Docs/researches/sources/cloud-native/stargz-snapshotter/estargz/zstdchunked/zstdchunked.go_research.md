## sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked.go

Purpose: implements zstd:chunked compression/decompression support under the `estargz.Compression` contract, including zstd skippable frames for TOC and footer plus annotations compatible with containers/storage zstd-chunked metadata.

Important APIs/types/functions: exported annotation constants are `ManifestChecksumAnnotation` and `ManifestPositionAnnotation`. `Decompressor.Reader` creates a zstd decoder for file payloads. `ParseTOC` zstd-decompresses the TOC JSON and computes its raw digest. `ParseFooter` decodes a 40-byte footer containing TOC offset, compressed length, raw size, manifest type, and magic. `DecompressTOC` returns a read closer for raw TOC JSON. `Compressor` holds `CompressionLevel`, optional `Metadata`, and a `sync.Pool` of zstd encoders. `Writer` reuses pooled encoders. `WriteTOCAndFooter` marshals TOC JSON, zstd-compresses it, writes a skippable-frame-wrapped TOC, writes a skippable-frame-wrapped footer, populates annotations when `Metadata` is non-nil, and returns raw TOC digest. `zstdFooterBytes` and `appendSkippableFrameMagic` encode the zstd-chunked frames.

Control flow: payload chunks are encoded as normal zstd frames. At close, compressed TOC is appended inside an 8-byte skippable-frame header; footer stores TOC position adjusted past that header and is itself appended as a skippable frame. Readers parse the trailing footer bytes from inside the final skippable frame, then range-read and decompress exactly the compressed TOC length.

State and persistence: compressor state includes reusable zstd encoders in a pool and optional metadata annotations written by side effect. The compressed blob persists TOC and footer frames; no separate state store is used.

Dependencies and integration points: uses `github.com/klauspost/compress/zstd`, `estargz` interfaces, and OCI digests. `fs/layer.Resolve` registers a `zstdchunked.Decompressor` as an additional metadata decompressor by default, making zstd-chunked layers mountable through the same reader path.

Risks: `ParseFooter` assumes the supplied byte slice is at least 40 bytes and indexes fixed ranges without a length check; callers are expected to provide `FooterSize` bytes. It validates magic but not manifest type or raw-size consistency. `WriteTOCAndFooter` stores `err` from `io.Copy` but continues to write the footer before returning it; if TOC copy failed, side effects may already have occurred. Encoder pooling requires `Close` to be called to return encoders.

Test signals: `zstdchunked_test.go` runs the shared compression suite across fastest/default/better compression levels, validates zstd frame offsets, computes DiffID through zstd decompression, and round-trips footer parse values.
