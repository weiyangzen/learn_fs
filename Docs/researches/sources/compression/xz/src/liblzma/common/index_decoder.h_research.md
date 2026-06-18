<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.h -->
# sources/compression/xz/src/liblzma/common/index_decoder.h

Purpose: Internal declaration header for the Index streaming decoder initializer.

Important API: Declares `lzma_index_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, lzma_index **i, uint64_t memlimit)`.

Control flow/state: No runtime state. The initializer plugs Index decoding into the liblzma `lzma_next_coder` pipeline and is wrapped by public stream and buffer APIs.

Dependencies/integration: Includes `common.h` and `index.h`. Used by `file_info.c` and `index_decoder.c`.

Risks/tests: Build/API synchronization and correct ownership contract for `lzma_index **i` are the relevant checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.h -->
