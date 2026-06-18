# sources/compression/xz/src/liblzma/common/block_buffer_decoder.c

Purpose: single-call decoder for one XZ Block payload, including compressed data, padding, and check, using an already decoded/populated `lzma_block`.

Important APIs/types/functions: public `lzma_block_buffer_decode(lzma_block *block, const lzma_allocator *allocator, const uint8_t *in, size_t *in_pos, size_t in_size, uint8_t *out, size_t *out_pos, size_t out_size)`.

Control flow: validates input/output pointer and position contracts, initializes a temporary `lzma_next_coder` with `lzma_block_decoder_init()`, saves starting positions, runs the decoder with `LZMA_FINISH`, converts `LZMA_STREAM_END` to `LZMA_OK`, maps incomplete decoding to `LZMA_DATA_ERROR` when input is exhausted or `LZMA_BUF_ERROR` when output is too small, restores positions on failure, and frees decoder state.

State and persistence: all state is temporary except successful updates to caller positions and `block` fields made by the block decoder. On errors, positions are restored, but nested decoder side effects inside `block` may need caller awareness.

Dependencies/integration: includes `block_decoder.h`; used by public single-call Block APIs documented in `api/lzma/block.h`.

Risks: assumes processing the final Block byte never produces output when distinguishing truncated input from full output. New filters with different end-marker behavior could challenge that assumption. Callers must provide a valid `block->filters` decoded from the Block Header.

Test signals: block buffer decode tests for valid blocks, truncated input, too-small output, bad check, bad padding, and invalid pointer/position arguments.
