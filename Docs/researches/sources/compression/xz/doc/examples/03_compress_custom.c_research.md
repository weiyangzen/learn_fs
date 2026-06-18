<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/03_compress_custom.c -->
# sources/compression/xz/doc/examples/03_compress_custom.c

Purpose: documented sample for building a custom filter chain with x86 BCJ followed by LZMA2.

Important APIs/types/functions: `init_encoder`, `lzma_lzma_preset`, `lzma_filter`, `LZMA_FILTER_X86`, `LZMA_FILTER_LZMA2`, `lzma_stream_encoder`, and the same multi-call `compress` loop as the easy example.

Control flow: initialize LZMA2 options from default preset, build a terminated filter array, create a CRC64 stream encoder, then stream stdin to stdout with `lzma_code`.

State and persistence: encoder state lives in `lzma_stream`; output is stdout.

Dependencies and integration: teaches liblzma filter-chain API and BCJ/LZMA2 ordering. Depends on builds that include both filters.

Risks: compression benefits only for x86 executable-like input. `LZMA_OPTIONS_ERROR` can occur in feature-reduced liblzma builds.

Test signals: compile and compress sample x86 binaries/plain text, validate stream with `xz -t`, and compare compression ratios to easy mode.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/03_compress_custom.c -->
