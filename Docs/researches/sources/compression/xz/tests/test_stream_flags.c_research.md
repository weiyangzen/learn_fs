# sources/compression/xz/tests/test_stream_flags.c

Purpose: tests `.xz` Stream Header/Footer encoding, decoding, and comparison.

Important constants and helpers: `XZ_STREAM_FLAGS_SIZE`, header magic bytes, footer magic bytes, `stream_header_encode_helper()`, `stream_footer_encode_helper()`, `stream_header_decode_helper()`, and `stream_footer_decode_helper()`.

Control flow: header/footer encode tests iterate check IDs, verify magic bytes, stream flag bits, backward-size encoding, CRC32, and footer magic; they reject unsupported versions, invalid check IDs, and invalid backward sizes where applicable. Decode tests round-trip encoded data, then mutate magic, reserved bits, upper check bits, stream flags, and CRC fields to assert `LZMA_FORMAT_ERROR`, `LZMA_OPTIONS_ERROR`, or `LZMA_DATA_ERROR`. Compare tests validate version, check, backward-size equality, `LZMA_VLI_UNKNOWN` handling, and invalid backward-size detection.

State and persistence: all buffers are stack-local. No files are used.

Dependencies and integration: uses liblzma stream flag APIs, CRC32, endian helpers, and build-gated encoder/decoder support. It protects the container-level metadata that decoders use before block processing.

Risks: stream flags are compact and CRC-protected; tests must recompute CRCs after intentional semantic mutations to ensure the intended validation layer fails. Some loops use `LZMA_CHECK_ID_MAX` boundaries, so API constant changes matter.

Test signals: byte-level validation of container metadata and robust corruption classification.
