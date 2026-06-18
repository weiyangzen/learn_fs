<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.h -->
# sources/compression/xz/src/liblzma/common/filter_decoder.h

Purpose: Internal declaration header for raw decoder chain initialization.

Important API: Declares `lzma_raw_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_filter *options)`.

Control flow/state: No runtime behavior; it exposes the initializer used by stream, block, and buffer wrappers while public API entry points remain in `filter_decoder.c`.

Dependencies/integration: Includes `common.h` for `lzma_next_coder`, allocator, and filter definitions. Used by raw buffer decoding and stream/block decode paths.

Risks/tests: Header risk is primarily API drift between declaration and implementation. Build coverage and raw decoder initialization tests catch regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.h -->
