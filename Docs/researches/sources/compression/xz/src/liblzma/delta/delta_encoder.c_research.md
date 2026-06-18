# sources/compression/xz/src/liblzma/delta/delta_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.c -->
## sources/compression/xz/src/liblzma/delta/delta_encoder.c

### Purpose
`delta_encoder.c` implements byte Delta encoding, filter-chain update forwarding, and Delta property encoding.

### Important APIs, Types, And Functions
`copy_and_encode()` encodes from input to output when Delta is first in the chain. `encode_in_place()` postprocesses output from a preceding filter. `delta_encode()` selects direct or chained mode. `delta_encoder_update()` forwards updates to the next filter because Delta options are immutable mid-stream. `lzma_delta_encoder_init()` installs callbacks, and `lzma_delta_props_encode()` writes the one-byte distance property.

### Control Flow
In direct mode, the encoder copies the minimum available input/output, subtracts the historical byte, updates history with original input, and returns stream end on flushing/finishing after all input is consumed. In chained mode, it calls the next coder first and subtracts history from the newly written output bytes in-place. Property encoding validates options through the shared memusage function and stores `dist - 1`.

### State, Persistence, And Dependencies
Streaming state is the 256-byte original-data history ring and distance. The file depends on common Delta initialization, next-filter update helpers, and allocator conventions.

### Integration Points
Delta can appear as a filter in raw or `.xz` encoder chains before LZMA/LZMA2. Property encoding is used by filter flags encoders.

### Risks
Mid-stream option changes are intentionally ignored for Delta and only forwarded downstream, so callers expecting distance changes will not get them. Direct mode must handle NULL input/output only when computed size is zero.

### Test Signals
Tests should cover direct and chained mode, all distance boundaries, partial buffers, flush/finish return codes, property encoding validation, and attempted option updates.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.c -->
