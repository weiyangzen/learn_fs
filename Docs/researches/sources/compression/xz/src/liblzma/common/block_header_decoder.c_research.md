# sources/compression/xz/src/liblzma/common/block_header_decoder.c

Purpose: decodes and validates XZ Block Headers into a caller-provided `lzma_block`, including CRC32 verification and filter option allocation.

Important APIs/types/functions: public `lzma_block_header_decode(lzma_block *block, const lzma_allocator *allocator, const uint8_t *in)`.

Control flow: validates pointers and caller-provided `header_size`/check type, clears the filter array to safe freeable values, downgrades unsupported future block versions to version 1, initializes `ignore_check`, verifies header CRC32, rejects unsupported flags, decodes optional compressed and uncompressed VLIs, decodes one to four Filter Flags entries, and requires all padding bytes to be zero.

State and persistence: mutates caller `lzma_block` fields and allocates filter option structures through `lzma_filter_flags_decode()`. On filter decode/padding errors it frees allocated filters.

Dependencies/integration: includes `common.h` and `check.h`; uses VLI decoder, filter flags decoder, CRC32, and Block size utilities. Stream decoders call it after reading the Block Header bytes.

Risks: header parsing is file-format attack surface. CRC, VLI, flag, padding, and allocation cleanup checks must remain strict. Fuzzing mode can bypass CRC failure for deeper parser coverage, so production guards must remain conditional.

Test signals: `test_block_header` and fuzzing corpora for bad CRCs, invalid VLIs, unsupported flags, bad padding, filter decode errors, and version downgrade behavior.
