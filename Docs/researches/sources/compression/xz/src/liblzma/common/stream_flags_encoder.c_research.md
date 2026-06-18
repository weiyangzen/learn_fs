# sources/compression/xz/src/liblzma/common/stream_flags_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_encoder.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_encoder.c

### Purpose
`stream_flags_encoder.c` writes `.xz` Stream Headers and Footers from `lzma_stream_flags`, including magic bytes, Stream Flags bytes, CRC32, and Footer Backward Size encoding.

### Important APIs, Types, And Functions
The private `stream_flags_encode()` writes the two-byte flags field. Public APIs are `lzma_stream_header_encode()` and `lzma_stream_footer_encode()`.

### Control Flow
Header encoding accepts only version `0`, copies header magic, writes reserved-zero byte plus Check ID, computes CRC32 over Stream Flags, and writes it little-endian. Footer encoding accepts only version `0`, validates `backward_size`, stores `(backward_size / 4) - 1`, writes Stream Flags, computes CRC32 over Backward Size plus flags, and appends Footer magic.

### State, Persistence, And Dependencies
There is no retained state. The output buffer receives exactly `LZMA_STREAM_HEADER_SIZE` bytes for both Header and Footer. Dependencies include `is_backward_size_valid()`, stream magic constants, `lzma_crc32`, and endian writers.

### Integration Points
Stream encoders call this file before Block output and after Index output. Correct Footer generation depends on Index size calculation by `lzma_index_size()`.

### Risks
Invalid Check IDs are treated as programming errors. Footer encoding requires a known, aligned Backward Size, so callers must not pass `LZMA_VLI_UNKNOWN`. Layout assertions protect the fixed 12-byte Header/Footer size.

### Test Signals
Tests should compare encoded bytes against known fixtures, mutate Check IDs and versions, validate Backward Size boundary handling, and round-trip through the decoder.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_encoder.c -->
