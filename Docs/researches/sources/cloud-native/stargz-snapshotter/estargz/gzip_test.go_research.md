## sources/cloud-native/stargz-snapshotter/estargz/gzip_test.go

Purpose: exercises regular gzip eStargz creation/parsing through the shared compression suite and directly validates footer encoding/parsing for modern and legacy footer layouts.

Important APIs and helpers: `TestGzipEStargz` runs `CompressionTestSuite` with controllers for `gzip.NoCompression`, `BestSpeed`, `BestCompression`, `DefaultCompression`, and `HuffmanOnly`. `gzipController` implements `TestingController` by combining `GzipCompressor` and `GzipDecompressor`, using `CheckGzipHasStreams` and `GzipDiffIDOf` for stream and DiffID checks. `TestGzipFooter` iterates offsets from 0 to 200000 and calls both `checkFooter` and `checkLegacyFooter`. `TestGzipParseFooterInvalidExtra` synthesizes malformed gzip blocks whose extra fields are nil, empty, or too short.

Control flow: suite cases build tar inputs, convert them to eStargz, compare TOC/tar equivalence, verify TOC digests, and test reads. Footer checks create bytes with `gzipFooterBytes` or `legacyFooterBytes`, parse them, and assert exact offsets. Invalid-extra tests pad a gzip block to `FooterSize` so the parser reaches extra validation.

State and persistence: in-memory byte buffers only; no file or network state.

Dependencies and integration points: depends on `compress/gzip` for test construction and on `testutil.go` for comprehensive archive behavior. Legacy footer helper mirrors the old footer format using `CreateGzipFooter`.

Risks: footer offset iteration is broad but not exhaustive for 64-bit values or corrupt magic strings. Invalid-extra coverage targets the modern parser only, not legacy parser or external TOC parser. Shared suite covers normal operation but not invalid compression-level constructor behavior.

Test signals: strong signal for gzip compatibility across compression levels, footer stability, legacy support, and safe handling of a previously panic-prone malformed extra-field class.
