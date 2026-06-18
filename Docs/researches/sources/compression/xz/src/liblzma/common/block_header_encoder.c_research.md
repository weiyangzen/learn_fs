# sources/compression/xz/src/liblzma/common/block_header_encoder.c

Purpose: computes and encodes XZ Block Headers from a configured `lzma_block`, including optional sizes, filter flags, padding, and CRC32.

Important APIs/types/functions: public `lzma_block_header_size(lzma_block *block)` and `lzma_block_header_encode(const lzma_block *block, uint8_t *out)`.

Control flow: `lzma_block_header_size()` validates version, sizes, and filter list, sums the fields and filter flag encoded sizes, enforces at most `LZMA_FILTERS_MAX` filters, and rounds `block->header_size` to a multiple of four. `lzma_block_header_encode()` validates block size, writes encoded header size and flags, encodes optional compressed/uncompressed sizes, encodes filter flags, zero-fills padding, and writes CRC32 over the header excluding the CRC field.

State and persistence: mutates only `block->header_size` in the size helper; encoding writes caller-provided output buffer.

Dependencies/integration: depends on VLI size/encode, filter flags size/encode, `lzma_block_unpadded_size()`, and `lzma_crc32()`. Used by stream and buffer encoders.

Risks: callers may intentionally reserve an oversized header, so size calculation does not fully validate final total Block size. Encoding requires `header_size` to be set and enough output space. Filter count and unknown-size handling must match format documentation.

Test signals: `test_block_header`, stream encode/decode round trips, headers with known/unknown sizes, multiple filters, padded headers, and CRC mutation tests.
