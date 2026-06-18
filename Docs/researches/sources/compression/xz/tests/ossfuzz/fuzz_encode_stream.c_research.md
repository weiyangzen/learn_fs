# sources/compression/xz/tests/ossfuzz/fuzz_encode_stream.c

Purpose: OSS-Fuzz target for `.xz` stream encoding with LZMA2 presets.

Important API: `LLVMFuzzerTestOneInput()` uses the first input byte as a preset selector, initializes `lzma_options_lzma`, creates a two-entry filter chain (`LZMA_FILTER_LZMA2`, terminator), starts `lzma_stream_encoder()` with `LZMA_CHECK_CRC64`, and passes the remaining bytes to `fuzz_code()`.

Control flow: empty input returns after printing a diagnostic. Only selected decider values are accepted to guide coverage toward valid preset levels: 0, 1, 5, and extreme variants derived from 6 and 7. Preset or encoder initialization failure aborts. All encoded output is discarded.

State and persistence: per-call encoder state only. It does not persist corpora or output streams.

Dependencies and integration: covers LZMA2 encoding, stream encoding, check generation, and action handling through the shared chunked helper.

Risks: the target deliberately limits the option space to presets, so it does not fuzz arbitrary filter-chain parsing or custom LZMA parameters. It still exercises critical compression paths with fuzzed payload bytes.

Test signals: crashes, sanitizer reports, and `LZMA_PROG_ERROR` aborts. Deterministic generated compression tests provide complementary round-trip correctness.
