<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.h -->
# sources/compression/xz/src/liblzma/common/stream_decoder.h

Purpose: Internal declaration header for `.xz` Stream decoder initialization.

Important API: Declares `lzma_stream_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, uint64_t memlimit, uint32_t flags)`.

Control flow/state: No runtime state. The initializer is used by the public stream decoder API, stream buffer decoder, auto decoders, and related wrappers.

Dependencies/integration: Includes `common.h`; implemented by `stream_decoder.c`.

Risks/tests: Flag contract and declaration synchronization are tested through stream decoder builds and API tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.h -->
