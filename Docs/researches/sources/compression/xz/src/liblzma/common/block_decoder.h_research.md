# sources/compression/xz/src/liblzma/common/block_decoder.h

Purpose: internal declaration header for initializing the streaming XZ Block decoder.

Important APIs/types/functions: declares `lzma_block_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, lzma_block *block)`.

Control flow: no implementation flow. The initializer installs a Block decoder into a `lzma_next_coder` chain for use by stream decoders or single-call helpers.

State and persistence: no header-owned state. Implementation allocates per-decoder state and nested raw filter decoder state.

Dependencies/integration: includes `common.h`. Consumed by `block_decoder.c`, `block_buffer_decoder.c`, and higher-level stream decoding code.

Risks: signature changes affect multiple decoder layers. The caller must pass a validated `lzma_block` with header size, check type, sizes, and filters correctly populated.

Test signals: build coverage for decoder-only and full builds; runtime coverage through block buffer and stream decoder tests.
