# sources/compression/xz/src/liblzma/lz/lz_encoder.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.h -->
## sources/compression/xz/src/liblzma/lz/lz_encoder.h

### Purpose
`lz_encoder.h` defines the generic LZ encoder input-window and match-finder API used by LZMA-family encoders.

### Important APIs, Types, And Functions
It defines `IS_ENC_DICT_SIZE_VALID`, `lzma_match`, `lzma_mf`, `lzma_lz_options`, `lzma_lz_encoder`, match-finder helper inlines (`mf_ptr`, `mf_avail`, `mf_unencoded`, `mf_position`, `mf_skip`, `mf_read`), `lzma_lz_encoder_init()`, `lzma_lz_encoder_memusage()`, `lzma_mf_find()`, and HC/BT finder prototypes.

### Control Flow
The inline helpers expose match-finder state transitions to LZMA encoders. `mf_skip()` calls the selected skip callback and increments read-ahead. `mf_read()` copies previously buffered uncompressed bytes for LZMA2 uncompressed chunks. `mf_position()` preserves low alignment bits even after window moves.

### State, Persistence, And Dependencies
`lzma_mf` is the key mutable state: window buffer, history limits, offset normalization base, read/write counters, pending flush bytes, hash and son tables, cyclic metadata, depth, nice length, match max, and current action. The header depends on `common.h`.

### Integration Points
LZMA encoder code uses this API for match discovery and to fall back to uncompressed chunk output. `lz_encoder_mf.c` implements the declared match-finder functions.

### Risks
Most fields are performance-critical and have implicit invariants. `read_ahead` means `read_pos` is not always the next unencoded byte. `cyclic_size` must be dictionary size plus one and below internal limits. Dictionary validation macro limits encoder dictionaries more than the decoder format permits.

### Test Signals
Unit tests around read-ahead accounting, `mf_read()` after incompressible chunks, and each match-finder callback validate this interface indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.h -->
