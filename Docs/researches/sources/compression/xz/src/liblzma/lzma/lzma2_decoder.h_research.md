# sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h -->
## sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h

### Purpose
`lzma2_decoder.h` declares internal LZMA2 decoder entry points for filter registration, memory accounting, and property parsing.

### Important APIs, Types, And Functions
It declares `lzma_lzma2_decoder_init()`, `lzma_lzma2_decoder_memusage()`, and `lzma_lzma2_props_decode()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `common.h`.

### Integration Points
Decoder filter tables include this header when LZMA2 decoder support is enabled.

### Risks
These internal functions must remain aligned with filter registration and property decoder expectations.

### Test Signals
Compile matrix tests and LZMA2 decoder/property tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h -->
