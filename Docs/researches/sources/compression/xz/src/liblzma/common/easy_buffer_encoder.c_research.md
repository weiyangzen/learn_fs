# sources/compression/xz/src/liblzma/common/easy_buffer_encoder.c

Purpose: public convenience API for single-call XZ Stream encoding using a preset level instead of an explicit filter chain.

Important APIs/types/functions: public `lzma_easy_buffer_encode(uint32_t preset, lzma_check check, const lzma_allocator *allocator, const uint8_t *in, size_t in_size, uint8_t *out, size_t *out_pos, size_t out_size)`.

Control flow: allocates a stack `lzma_options_easy`, calls `lzma_easy_preset()` to translate preset flags/level into an LZMA2 filter chain, returns `LZMA_OPTIONS_ERROR` on invalid preset, then delegates to `lzma_stream_buffer_encode()` with the generated filters and requested check.

State and persistence: no persistent state; filter options live on the stack for the duration of the call and are consumed synchronously by the stream buffer encoder.

Dependencies/integration: includes `easy_preset.h`; depends on stream buffer encoder and check support. Publicly documented as the easy single-call path.

Risks: stack-owned filter options are safe only because encoding is synchronous. Invalid checks are handled by the delegated stream encoder. Preset translation must stay compatible with `lzma_easy_encoder()`.

Test signals: single-call encode/decode round trips for all presets, invalid preset errors, unsupported check errors, and exact/too-small output buffers.
