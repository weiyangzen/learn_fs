# sources/compression/xz/src/liblzma/common/stream_flags_decoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_decoder.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_decoder.c

### Purpose
`stream_flags_decoder.c` decodes `.xz` Stream Headers and Footers into `lzma_stream_flags`, verifying magic bytes, CRC32, reserved bits, Check ID, and Footer Backward Size.

### Important APIs, Types, And Functions
The private `stream_flags_decode()` interprets the two Stream Flags bytes. Public APIs are `lzma_stream_header_decode()` and `lzma_stream_footer_decode()`.

### Control Flow
Header decoding checks the six-byte magic, verifies CRC32 over Stream Flags, decodes flags, and sets `backward_size` to `LZMA_VLI_UNKNOWN` because the Header does not contain it. Footer decoding checks the two-byte Footer magic at the end, verifies CRC32 over Backward Size plus Stream Flags, decodes flags, and converts the stored `(backward_size / 4) - 1` representation back to bytes. Under fuzzing builds, CRC mismatches can be ignored to let fuzzers reach deeper paths.

### State, Persistence, And Dependencies
There is no retained state. The file depends on stream magic constants, `lzma_crc32`, endian readers, and public format constants.

### Integration Points
Stream decoders use these functions to identify `.xz` streams, distinguish format errors from data errors, and later compare Header/Footer flags with `lzma_stream_flags_compare()`.

### Risks
CRC bypass under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION` must never be enabled in production. Reserved-bit validation is strict; future format versions would currently report options errors. Footer size conversion assumes the fixed `.xz` Footer layout.

### Test Signals
Tests should include valid Header/Footer pairs, bad magic, bad CRC, reserved flag bits, every supported Check ID, Footer Backward Size decoding, and fuzzing-mode-specific CRC behavior if that build mode is used.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_decoder.c -->
