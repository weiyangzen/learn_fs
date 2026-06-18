# sources/compression/xz/src/liblzma/common/easy_encoder_memusage.c

Purpose: public helper returning encoder memory usage for an easy preset.

Important APIs/types/functions: public `lzma_easy_encoder_memusage(uint32_t preset)`.

Control flow: calls `lzma_easy_preset()` into stack options and returns `UINT32_MAX` for invalid presets. For valid presets, delegates to `lzma_raw_encoder_memusage(opt_easy.filters)`.

State and persistence: no persistent state.

Dependencies/integration: includes `easy_preset.h`; depends on raw encoder memory-usage code and preset-to-filter translation. Applications can use it before allocating or choosing compression settings.

Risks: numeric sentinel must not be mistaken for a valid memory usage. Results must stay aligned with the actual filter options used by `lzma_easy_encoder()` and `lzma_easy_buffer_encode()`.

Test signals: expected memory usage for all preset levels, invalid-preset sentinel behavior, and consistency with raw encoder memusage for filters returned by `lzma_easy_preset()`.
