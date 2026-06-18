<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.c -->
# sources/compression/xz/src/liblzma/common/index_encoder.c

Purpose: Implements streaming and single-call encoding of an `lzma_index` into the `.xz` Index field.

Important APIs/types: `lzma_index_coder` tracks sequence, source Index, `lzma_index_iter`, VLI position, and CRC32. APIs include internal `lzma_index_encoder_init()`, public `lzma_index_encoder()`, and public `lzma_index_buffer_encode()`.

Control flow: The encoder emits Index Indicator, record count, each Block's Unpadded Size and Uncompressed Size from `lzma_index_iter_next()`, padding bytes from `lzma_index_padding_size()`, and CRC32. CRC is updated once per call over bytes produced before the CRC field.

State and persistence: Streaming state persists sequence, iterator, VLI position, and CRC across calls. The input `lzma_index` is borrowed, not owned, so callers must keep it alive while the coder runs.

Dependencies/integration: Depends on `index_encoder.h`, `index.h`, `check.h`, VLI encoding, and iterator APIs from `index.c`. Used by stream buffer encoding and public Index encoding.

Risks/tests: `lzma_index_buffer_encode()` preflights `lzma_index_size(i)` and restores output position on unexpected failure. Tests should cover empty Index, multi-record Index, exact buffer sizing, undersized output, CRC bytes, and streaming calls that split in the middle of VLIs and CRC.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.c -->
