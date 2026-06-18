## sources/cloud-native/containers-storage/pkg/chunked/zstdchunked_test.go

Purpose: Linux integration-style tests for zstd:chunked manifest writing and reading plus tar type conversion.

Important APIs/types/functions: `seekable`, `someFiles`, `TestGenerateAndParseManifest`, and `TestGetTarType`.

Control flow: builds a tar stream from sample metadata, produces tar-split data, compresses it, writes a zstd:chunked manifest with annotations, parses annotation offsets, serves the manifest/tar-split frames through a mock seekable source, calls `readZstdChunkedManifest`, and compares decoded TOC JSON. The tar type test checks both chunked `typeToTarType` and minimal `GetType`.

State and persistence: all data is in buffers except temporary directory passed to manifest reader.

Dependencies and integration points: connects `minimal.WriteZstdChunkedManifest`, `toc.GetTOCDigest`, zstd compression, tar-split, and manifest reader code outside the selected files.

Risks: sample metadata is small and does not cover chunk arrays, zeros chunks, xattrs, or large tar-split frames. The mock requires exactly two range requests, so it tests one expected read shape.

Test signals: good end-to-end signal for annotation offset math and TOC digest round-trip. Local execution unavailable because `go` is missing.
