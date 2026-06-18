# sources/compression/xz/src/liblzma/api/lzma/block.h

Purpose: declares public APIs for encoding, decoding, sizing, and validating individual `.xz` Blocks and Block Headers.

Important APIs/types/functions: defines `lzma_block` with version, header size, check type, compressed/uncompressed sizes, filter chain, raw check bytes, reserved ABI fields, and `ignore_check`. Declares `lzma_block_header_size_decode`, `lzma_block_header_size`, `lzma_block_header_encode/decode`, `lzma_block_compressed_size`, `lzma_block_unpadded_size`, `lzma_block_total_size`, `lzma_block_encoder/decoder`, `lzma_block_buffer_bound`, `lzma_block_buffer_encode`, `lzma_block_uncomp_encode`, and `lzma_block_buffer_decode`.

Control flow: callers prepare an `lzma_block`, size or decode the header, run streamed block coder via `lzma_code()` or use single-call buffer APIs, then use computed sizes and `raw_check` for Index and integrity handling. Block Header and Block Data are intentionally separate for advanced container handling.

State and persistence: streamed coders update `compressed_size`, `uncompressed_size`, and `raw_check` during/after coding. Header decode allocates filter options into caller-provided filter arrays and does not free old options.

Dependencies/integration: relies on `lzma_filter`, `lzma_check`, and `lzma_vli`. Stream encoders/decoders, index generation, random access, and tests for block headers use these APIs.

Risks: `filters` arrays must have `LZMA_FILTERS_MAX + 1` entries or header decode can overflow the caller buffer. `check` must come from Stream Flags when decoding. `ignore_check` weakens integrity validation and requires `version >= 1`. Size fields use `LZMA_VLI_UNKNOWN` semantics and need careful validation.

Test signals: `tests/test_block_header.c`, block buffer encode/decode tests, random-access/index tests, and round-trip `.xz` stream tests.
