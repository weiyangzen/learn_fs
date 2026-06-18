# sources/compression/xz/src/liblzma/common/easy_preset.c

Purpose: translates public easy preset values into concrete LZMA2 filter options used by easy encoder and memory-usage helpers.

Important APIs/types/functions: internal `lzma_easy_preset(lzma_options_easy *opt_easy, uint32_t preset)`.

Control flow: masks the preset level from optional flags, validates that the level is at most 9 and only supported flags are present, initializes `opt_easy->opt_lzma` using `lzma_lzma_preset()`, and builds a two-entry filter chain: `LZMA_FILTER_LZMA2` with the options followed by `LZMA_VLI_UNKNOWN`.

State and persistence: writes caller-provided `lzma_options_easy`, including embedded LZMA options and filter array pointers to that embedded storage. No global state.

Dependencies/integration: includes `easy_preset.h`; used by easy stream/buffer encoders and encoder/decoder memory-usage helpers.

Risks: filter option pointers refer to fields inside `lzma_options_easy`, so the structure must outlive immediate consumers. Preset flag validation must stay synchronized with the public API. Changes alter compression behavior and memory usage for widely used presets.

Test signals: preset validity tests, expected option fields for levels and extreme flag, and consistency across easy encoder and memusage APIs.
