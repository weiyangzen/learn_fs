# sources/compression/xz/src/liblzma/lzma/lzma_common.h Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_common.h -->
## sources/compression/xz/src/liblzma/lzma/lzma_common.h

### Purpose
`lzma_common.h` defines private constants, state transitions, and probability-table helpers shared by LZMA encoder and decoder implementations.

### Important APIs, Types, And Functions
It defines position-state limits, `is_lclppb_valid()`, the 12-state `lzma_lzma_state` enum, state update macros (`update_literal`, `update_match`, `update_long_rep`, `update_short_rep`), literal coder sizing and selection macros, `literal_init()`, match length constants, distance-state constants, distance-slot ranges, alignment constants, and repeat-distance count.

### Control Flow
The macros encode LZMA's finite-state model: recent literal/match/repetition events update state, and `is_literal_state()` chooses literal coding context. `literal_subcoder()` selects one of many literal probability subcoders from position bits and previous-byte context. `literal_init()` resets all literal probabilities with `bit_reset()`.

### State, Persistence, And Dependencies
The header defines no standalone objects, but it describes the layout and transitions for probability arrays and coder state maintained by LZMA encoder/decoder files. It depends on `common.h` and `range_common.h`.

### Integration Points
LZMA1 and LZMA2 encoder/decoder cores include this header to share format constants and guarantee identical state-machine behavior.

### Risks
These constants are format-defining. Any mismatch between encoder and decoder state updates or length/distance constants breaks compatibility. `literal_mask_calc()` and `literal_subcoder()` rely on `lc + lp <= LZMA_LCLP_MAX`.

### Test Signals
Known-answer LZMA streams, property validation for `lc/lp/pb`, literal probability initialization checks, and distance/length boundary encoding tests validate this shared definition layer.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_common.h -->
