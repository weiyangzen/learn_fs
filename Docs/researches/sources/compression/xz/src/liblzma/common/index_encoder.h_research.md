<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.h -->
# sources/compression/xz/src/liblzma/common/index_encoder.h

Purpose: Internal declaration header for Index encoder initialization.

Important API: Declares `lzma_index_encoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_index *i)`.

Control flow/state: No runtime state. Exposes the streaming Index encoder to stream/block container code while keeping public wrappers in `index_encoder.c`.

Dependencies/integration: Includes `common.h`; implemented by `index_encoder.c`.

Risks/tests: Declaration drift is caught by build and Index encode tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.h -->
