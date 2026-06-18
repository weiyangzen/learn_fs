<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.h -->
# sources/compression/xz/src/liblzma/common/filter_common.h

Purpose: Internal header defining the common ABI prefix for encoder and decoder filter tables and declaring shared raw-filter helper functions.

Important APIs/types: `lzma_filter_coder` contains the common leading fields `id`, `init`, and `memusage`. `lzma_filter_find` is a function pointer returning that common view for a filter ID. Declarations cover `lzma_validate_chain()`, `lzma_raw_coder_init()`, and `lzma_raw_coder_memusage()`.

Control flow and state: The header has no runtime state. Its main design point is structural compatibility: encoder and decoder table structs begin with identical fields so `filter_common.c` can initialize and measure either side through the same interface.

Dependencies and integration: Includes `common.h` and is consumed by `filter_common.c`, `filter_encoder.c`, and `filter_decoder.c`.

Risks and tests: Adding fields before the common prefix in encoder or decoder structs would break casts used by `coder_find()`. Compile-time review and raw encoder/decoder init tests are the main signals.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.h -->
