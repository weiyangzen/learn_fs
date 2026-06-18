# sources/compression/xz/src/liblzma/common/easy_decoder_memusage.c

Purpose: public helper returning decoder memory usage for streams encoded with an easy preset.

Important APIs/types/functions: public `lzma_easy_decoder_memusage(uint32_t preset)`.

Control flow: translates the preset through `lzma_easy_preset()`. If invalid, returns `UINT32_MAX` as the documented error sentinel. Otherwise returns `lzma_raw_decoder_memusage(opt_easy.filters)`.

State and persistence: no persistent state; uses stack `lzma_options_easy`.

Dependencies/integration: includes `easy_preset.h` and depends on raw decoder memory-usage calculation. Used by applications to size memory limits before decoding data created with an easy encoder setting.

Risks: the sentinel is a numeric value, not an `lzma_ret`, so callers must distinguish it from real usage. Decoder usage depends on the generated filter chain and must remain aligned with preset definitions.

Test signals: verify all presets return expected non-sentinel values, invalid presets return `UINT32_MAX`, and values match raw decoder memory usage for the same filters.
