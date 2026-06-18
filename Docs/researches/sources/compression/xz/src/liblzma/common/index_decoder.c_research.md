<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.c -->
# sources/compression/xz/src/liblzma/common/index_decoder.c

Purpose: Implements streaming and single-call decoding of the `.xz` Index field into an `lzma_index`.

Important APIs/types: `lzma_index_coder` tracks sequence, memory limit, target index, output pointer, remaining record count, current VLI fields, VLI position, and CRC32. APIs include internal `lzma_index_decoder_init()`, public `lzma_index_decoder()`, and public `lzma_index_buffer_decode()`.

Control flow: The state machine reads `INDEX_INDICATOR`, VLI record count, memory usage check, repeated Unpadded and Uncompressed sizes, Index Padding, and little-endian CRC32. It preallocates record storage after count is known and updates CRC incrementally across calls. On stream completion it transfers ownership by assigning `*index_ptr` and nulling `coder->index`.

State and persistence: Before success, the decoder owns the in-progress `lzma_index` and frees it on reset/end/error. `memconfig` reports `lzma_index_memusage(1, coder->count)` and can raise/lower the limit if current known usage fits.

Dependencies/integration: Depends on `index_decoder.h`, `index.h`, `check.h`, VLI decode, and `lzma_index_append()`. `file_info.c` uses this decoder for reverse metadata parsing.

Risks/tests: Single-call decode restores `*in_pos` and frees partial Index on error, and reports required memory through `*memlimit` on `LZMA_MEMLIMIT_ERROR`. Tests should cover bad indicator, truncated VLI, count over memlimit, invalid Unpadded Size, bad padding, bad CRC, zero-record Index, and fuzzing-mode CRC bypass behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.c -->
