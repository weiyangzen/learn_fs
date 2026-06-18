# sources/compression/xz/src/liblzma/delta/delta_common.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.h -->
## sources/compression/xz/src/liblzma/delta/delta_common.h

### Purpose
`delta_common.h` declares shared Delta filter support used by public encoder/decoder headers and private implementation files.

### Important APIs, Types, And Functions
It includes `common.h` and declares `lzma_delta_coder_memusage()`.

### Control Flow
There is no control flow.

### State, Persistence, And Dependencies
The header introduces no state and depends on liblzma common types.

### Integration Points
Delta encoder and decoder headers include this file so filter registration can reference the shared memory-usage validator.

### Risks
Keeping only the memusage declaration public to Delta internals keeps initialization details private; external modules needing `lzma_delta_coder_init()` must include `delta_private.h`.

### Test Signals
Build tests catch declaration/definition drift; runtime tests exercise the function through encoder/decoder option validation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.h -->
