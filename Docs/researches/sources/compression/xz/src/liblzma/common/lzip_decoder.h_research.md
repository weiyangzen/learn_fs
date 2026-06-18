<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.h -->
# sources/compression/xz/src/liblzma/common/lzip_decoder.h

Purpose: Internal declaration header for lzip decoder initialization.

Important API: Declares `lzma_lzip_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, uint64_t memlimit, uint32_t flags)`.

Control flow/state: No runtime state; the initializer is used by public lzip decoder setup and generic auto-decoding paths.

Dependencies/integration: Includes `common.h` and is implemented by `lzip_decoder.c`.

Risks/tests: Header drift and flag contract mismatches are caught by build and lzip decode tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.h -->
