## sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression_test.go

Purpose: validates the binary footer layout emitted by `footerDataToBlob`.

Important APIs/types/functions: `TestGenerateAndReadFooter` and local helper `readFooterDataFromBlob`, which decodes the little-endian footer fields and checks `ZstdChunkedFrameMagic`.

Control flow: builds a `ZstdChunkedFooterData`, serializes it, asserts `FooterSizeSupported`, decodes all seven uint64 fields, validates the magic suffix, and compares with the original struct.

State and persistence: no filesystem or persistent state; all data is in memory.

Dependencies and integration points: directly protects the footer contract used by zstd:chunked writers. It uses `testify/assert`, `encoding/binary`, and the package constants.

Risks: the decoder helper lives only in the test because production code currently does not read the footer; tests do not cover manifest compression, annotations, or tar-split digest.

Test signals: good regression signal for footer field order, supported size, and magic bytes. Local execution was blocked because the Go toolchain is absent.
