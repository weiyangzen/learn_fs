# sources/compression/xz/src/liblzma/delta/delta_private.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_private.h -->
## sources/compression/xz/src/liblzma/delta/delta_private.h

### Purpose
`delta_private.h` defines the shared private state structure for Delta encoder and decoder implementations.

### Important APIs, Types, And Functions
`lzma_delta_coder` contains the next coder, Delta distance, ring position, and `history[LZMA_DELTA_DIST_MAX]`. It also declares `lzma_delta_coder_init()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
The state captures streaming history of original decoded bytes. It depends on `delta_common.h` for common liblzma types and constants.

### Integration Points
Delta encoder and decoder implementation files include this header to share initialization and state layout.

### Risks
The history buffer size must remain consistent with valid Delta distances and with modulo indexing in encoder/decoder loops. Changing the struct affects both directions.

### Test Signals
Round-trip tests across distance 1 and 256 and sanitizer runs with partial buffers are good signals for state layout correctness.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_private.h -->
