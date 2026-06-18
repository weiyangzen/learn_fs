# sources/compression/xz/src/liblzma/api/lzma/stream_flags.h

Purpose: declares `.xz` Stream Header/Footer flag structure and encode/decode/compare APIs.

Important APIs/types/functions: defines fixed `LZMA_STREAM_HEADER_SIZE` of 12 bytes; declares `lzma_stream_flags` with `version`, `backward_size`, `check`, and reserved ABI fields; defines backward size min/max; exports `lzma_stream_header_encode`, `lzma_stream_footer_encode`, `lzma_stream_header_decode`, `lzma_stream_footer_decode`, and `lzma_stream_flags_compare`.

Control flow: stream encoders encode a header from check flags and a footer from check plus backward Index size. Decoders parse header/footer, then compare flags while optionally ignoring unknown header backward size (`LZMA_VLI_UNKNOWN`).

State and persistence: no persistent state. Decoders populate caller-owned `lzma_stream_flags`.

Dependencies/integration: Stream encoders/decoders, Index validation, block decoders, and list/test modes use this to bind check type and backward Index size. CRC32 from `check.h` validates header/footer integrity.

Risks: nonzero version is currently unsupported for encoding and must be checked after decoding. Footer/header `LZMA_FORMAT_ERROR` means different things depending on stream position; callers should distinguish first-stream recognition from later corruption.

Test signals: `tests/test_stream_flags.c` verifies header/footer encoding, CRCs, invalid magic, backward-size validation, and comparisons.
