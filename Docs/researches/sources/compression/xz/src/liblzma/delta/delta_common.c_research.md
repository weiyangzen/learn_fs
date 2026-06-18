# sources/compression/xz/src/liblzma/delta/delta_common.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.c -->
## sources/compression/xz/src/liblzma/delta/delta_common.c

### Purpose
`delta_common.c` implements shared initialization, teardown, and option validation for the Delta encoder and decoder.

### Important APIs, Types, And Functions
`lzma_delta_coder_init()` allocates/reuses `lzma_delta_coder`, validates options, initializes distance, position, history, and the next filter. `lzma_delta_coder_memusage()` validates `lzma_options_delta` and returns coder size. `delta_coder_end()` frees chained coders and the Delta coder.

### Control Flow
Initialization allocates the coder on first use, installs the common end function, validates that options describe byte-type Delta with distance in range, resets `pos` and `history`, then initializes the next filter in the chain. Memusage returns `UINT64_MAX` for invalid options.

### State, Persistence, And Dependencies
Delta state is `distance`, one-byte `pos`, 256-byte history, and the `next` coder. There is no persistence beyond streaming history. Dependencies include `delta_private.h`, allocator helpers, and filter-chain initialization.

### Integration Points
Both encoder and decoder wrappers call this after installing their `code` callback. Filter registration uses the memusage function to validate options.

### Risks
History reset on initialization is essential; reuse without reset would corrupt streams. Only byte-wise Delta is supported, so future Delta types must extend validation and encode/decode loops.

### Test Signals
Tests should validate option rejection, distance boundaries, coder reuse after reinit, history reset between streams, and chaining with another filter.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.c -->
