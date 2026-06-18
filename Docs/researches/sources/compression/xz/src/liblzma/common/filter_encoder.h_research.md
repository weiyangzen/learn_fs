<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.h -->
# sources/compression/xz/src/liblzma/common/filter_encoder.h

Purpose: Internal declaration header for raw encoder chain initialization.

Important API: Declares `lzma_raw_encoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_filter *filters)`.

Control flow/state: The header has no runtime state. It lets buffer, block, stream, and MicroLZMA-style code initialize encoder chains without going through public `lzma_stream` setup.

Dependencies/integration: Includes `common.h`; implemented in `filter_encoder.c`.

Risks/tests: API drift is the main concern. Build tests and raw encoder tests validate the declaration remains synchronized.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.h -->
