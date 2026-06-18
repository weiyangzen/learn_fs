## sources/cloud-native/stargz-snapshotter/estargz/gzip.go

Purpose: provides the default gzip-based `Compression` implementation for creating and parsing eStargz layers, including modern and legacy footer formats and TOC decompression.

Important APIs/types/functions: `gzipCompression` embeds `GzipCompressor` and `GzipDecompressor`. `NewGzipCompressor` and `NewGzipCompressorWithLevel` expose compressor construction. `GzipCompressor.Writer` returns `gzip.NewWriterLevel` as a `WriteFlushCloser`. `WriteTOCAndFooter` marshals `JTOC`, writes it as a tar entry named `stargz.index.json` into a gzip stream, optionally tees uncompressed TOC tar bytes into `diffHash`, writes the 51-byte eStargz footer, and returns the raw TOC JSON digest. `gzipFooterBytes` and `CreateGzipFooter` encode the footer extra field. `GzipDecompressor.ParseFooter` validates `SG` subfield metadata and extracts the hex TOC offset. `LegacyGzipDecompressor` supports the older 47-byte footer layout. `parseTOCEStargz` and `decompressTOCEStargz` decompress the TOC gzip stream, read the first tar entry, verify its name, and JSON-decode the TOC while computing its digest.

Control flow: writers emit chunk gzip members elsewhere, call `WriteTOCAndFooter` at close, and append a final zero-length gzip stream with a footer extra field pointing to TOC. Readers read the fixed-size footer, parse the TOC offset, range-read the TOC gzip member, decode the tar-contained JSON, and return both `JTOC` and digest for verification.

State and persistence: compressor instances only store compression level. Generated footers and TOC bytes are written to the supplied `io.Writer`; no internal durable state is retained. The parsed TOC is returned to caller-owned metadata/readers.

Dependencies and integration points: depends on Go gzip/tar/binary/json packages and `opencontainers/go-digest`. Implements the interfaces declared in `types.go`, used by `estargz.Build`, `Open`, metadata readers, and layer resolver defaults. `CreateGzipFooter` is reused by the external-TOC implementation.

Risks: `gzip.NewWriterLevel` errors are ignored in `Writer` callers and in `WriteTOCAndFooter` for the TOC writer; invalid compression levels could panic later through a nil writer if allowed. `ParseFooter` now guards `len(extra) < 4`, but after validating subfield length it assumes `subfield` is long enough; gzip extra consistency normally enforces this, but hostile footers are a risk area. Legacy parsing is maintained for compatibility and expands the accepted surface.

Test signals: `gzip_test.go` runs the shared compression suite across no-compression, best-speed, best-compression, default, and Huffman-only levels; it also round-trips modern and legacy footer offsets and verifies invalid short extra fields return errors rather than panics.
