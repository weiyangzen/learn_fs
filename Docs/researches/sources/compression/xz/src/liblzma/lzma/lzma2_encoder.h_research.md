# sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h -->
## sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h

### Purpose
`lzma2_encoder.h` declares internal LZMA2 encoder APIs and chunk-size constants.

### Important APIs, Types, And Functions
It defines `LZMA2_CHUNK_MAX`, `LZMA2_UNCOMPRESSED_MAX`, `LZMA2_HEADER_MAX`, and `LZMA2_HEADER_UNCOMPRESSED`, and declares `lzma_lzma2_encoder_init()`, `lzma_lzma2_encoder_memusage()`, `lzma_lzma2_props_encode()`, and `lzma_lzma2_block_size()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `common.h`.

### Integration Points
LZMA2 encoder implementation and filter registration include this header. Multithreaded stream encoding uses block-size estimation through the declared API.

### Risks
Chunk constants must match the LZMA2 format and the encoder buffer layout. Changing them requires coordinated changes in decoder and tests.

### Test Signals
Boundary tests at chunk and uncompressed-size maxima validate use of these constants.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h -->
