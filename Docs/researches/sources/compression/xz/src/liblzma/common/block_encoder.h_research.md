# sources/compression/xz/src/liblzma/common/block_encoder.h

Purpose: internal Block encoder declarations and size limit constants shared by streaming and buffer Block encoders.

Important APIs/types/functions: defines `COMPRESSED_SIZE_MAX`, which reserves space for maximum Block Header and Check while keeping total encoded size within `LZMA_VLI_MAX`, and declares `lzma_block_encoder_init()`.

Control flow: no implementation flow. The constant feeds bound calculations and overflow checks; the initializer installs a Block encoder into a `lzma_next_coder`.

State and persistence: no header state.

Dependencies/integration: includes `common.h`. Used by `block_encoder.c`, `block_buffer_encoder.c`, and code that needs the maximum compressed-data size.

Risks: `COMPRESSED_SIZE_MAX` is part of Block size safety. Changing `LZMA_BLOCK_HEADER_SIZE_MAX`, `LZMA_CHECK_SIZE_MAX`, or VLI limits requires revalidating this expression. The initializer expects valid check and filter configuration from callers.

Test signals: compilation in encoder builds and boundary tests around maximum compressed/uncompressed Block sizes and buffer-bound calculations.
