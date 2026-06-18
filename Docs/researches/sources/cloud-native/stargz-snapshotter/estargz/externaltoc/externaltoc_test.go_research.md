## sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc_test.go

Purpose: validates the external-TOC gzip compression implementation against the same behavioral contract as regular gzip eStargz, plus a footer-specific check for the external TOC marker.

Important APIs and helpers: `TestGzipEStargz` constructs an `estargz.TestRunner` and passes multiple `gzipControllerWithLevel` factories into `estargz.CompressionTestSuite`. Each controller pairs a compressor with a decompressor whose provider calls `compressor.WriteTOCTo`, proving the compressor's out-of-band TOC buffer can feed parser paths. `TestGzipFooter` checks `gzipFooterBytes`, `FooterSize`, and `GzipDecompressor.ParseFooter`.

Control flow: the shared suite builds archives, opens them with the external decompressor, verifies DiffID/TOC/chunk contents, and checks stream locations. The footer test builds one footer, parses it, and requires `tocOffset == -1`.

State and persistence: test state is in-memory only. The provider closure intentionally captures the same compressor instance so `WriteTOCAndFooter` populates `buf` before `ParseTOC` asks for it.

Dependencies and integration points: integrates external TOC implementation with package-wide `CompressionTestSuite`, `CheckGzipHasStreams`, and `GzipDiffIDOf` from `estargz/testutil.go`. It indirectly exercises `Build`, `Open`, TOC verification, chunk digest checks, and lossless/lossy writer paths.

Risks: the tests do not cover malformed short gzip extra fields, nil provider behavior, provider errors, repeated provider calls after failure, missing `WriteTOCAndFooter`, or a non-nil reader being passed to `ParseTOC`. Because the suite uses a cooperative provider, real registry/annotation wiring for external TOC is outside this file's coverage.

Test signals: strong compatibility signal for normal external TOC archives across gzip levels; narrow direct signal that the footer advertises external TOC by returning negative offsets.
