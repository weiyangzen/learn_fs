# sources/compression/xz/src/liblzma/delta/delta_decoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.h -->
## sources/compression/xz/src/liblzma/delta/delta_decoder.h

### Purpose
`delta_decoder.h` declares Delta decoder entry points for liblzma filter registration and property parsing.

### Important APIs, Types, And Functions
It declares `lzma_delta_decoder_init()` and `lzma_delta_props_decode()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `delta_common.h`.

### Integration Points
Filter decoder tables include this header to initialize Delta decode chains and parse stored filter properties.

### Risks
The declarations expose internal liblzma functions, not public API. Signature drift would break filter registration builds.

### Test Signals
Compile tests and decoder/property round-trip tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.h -->
