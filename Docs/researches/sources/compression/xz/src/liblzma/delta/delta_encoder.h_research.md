# sources/compression/xz/src/liblzma/delta/delta_encoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.h -->
## sources/compression/xz/src/liblzma/delta/delta_encoder.h

### Purpose
`delta_encoder.h` declares Delta encoder entry points for filter-chain construction and property serialization.

### Important APIs, Types, And Functions
It declares `lzma_delta_encoder_init()` and `lzma_delta_props_encode()`.

### Control Flow
There is no runtime control flow.

### State, Persistence, And Dependencies
No state is defined. It depends on `delta_common.h`.

### Integration Points
Encoder filter tables include this header when Delta encoder support is compiled.

### Risks
These are internal declarations; mismatches with filter tables or conditionals cause build/link failures.

### Test Signals
Compile matrix and Delta encode/property tests validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.h -->
