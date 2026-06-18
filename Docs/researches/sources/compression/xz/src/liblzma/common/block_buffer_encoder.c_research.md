# sources/compression/xz/src/liblzma/common/block_buffer_encoder.c

Purpose: single-call XZ Block encoder that tries normal compression and falls back to uncompressed LZMA2 chunks when compressed output would not fit or would be larger than the guaranteed bound.

Important APIs/types/functions: `HEADERS_BOUND`, `lzma2_bound()`, internal `lzma_block_buffer_bound64()`, public `lzma_block_buffer_bound()`, `block_encode_uncompressed()`, `block_encode_normal()`, `block_buffer_encode()`, public `lzma_block_buffer_encode()`, and compatibility/public `lzma_block_uncomp_encode()`.

Control flow: bound helpers compute worst-case size including Block Header, padding, and Check. Encoding validates block/check/filter arguments, aligns available output to a four-byte Block boundary, reserves Check space, sets uncompressed/compressed sizes, tries raw filter compression with reserved header space, and on `LZMA_BUF_ERROR` writes valid LZMA2 uncompressed chunks instead. It pads compressed data to four bytes and appends the selected integrity check.

State and persistence: mutates caller `lzma_block` with actual filters used, header size, compressed/uncompressed sizes, and raw check. Temporary raw encoder state is always freed.

Dependencies/integration: includes block/filter/LZMA2 encoder and check headers. It supports symbol-version aliases for compatibility with older patched liblzma binaries.

Risks: output bound and overflow checks are security-sensitive. Fallback temporarily replaces `block->filters`, so restoration on every error path matters. Check support must be validated before encoding. Symbol-version compatibility must not alter default ABI.

Test signals: buffer-bound tests, incompressible fallback tests, exact-size output buffers, unsupported check errors, symbol-version builds, and decode round trips for both compressed and uncompressed fallback output.
