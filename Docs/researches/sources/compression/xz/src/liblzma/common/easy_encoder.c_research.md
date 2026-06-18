# sources/compression/xz/src/liblzma/common/easy_encoder.c

Purpose: public convenience initializer for streaming XZ encoding with a preset compression level and integrity check.

Important APIs/types/functions: public `lzma_easy_encoder(lzma_stream *strm, uint32_t preset, lzma_check check)`.

Control flow: translates `preset` into stack `lzma_options_easy` via `lzma_easy_preset()`, returns `LZMA_OPTIONS_ERROR` on invalid presets, and otherwise calls `lzma_stream_encoder(strm, opt_easy.filters, check)`.

State and persistence: this file owns no persistent state; the delegated stream encoder copies/initializes the needed filter options into `strm->internal`.

Dependencies/integration: includes `easy_preset.h`; relies on stream encoder, LZMA2 encoder, and check validation. Used by applications and the `xz` frontend for simple compression setup.

Risks: because filter options are stack-local, `lzma_stream_encoder()` must complete all initialization synchronously and not retain invalid stack pointers. Check support errors are delegated and may differ from preset errors.

Test signals: streaming round trips for presets 0-9 and extreme flag, invalid preset handling, unsupported check behavior, and action sequencing through `lzma_code()`.
