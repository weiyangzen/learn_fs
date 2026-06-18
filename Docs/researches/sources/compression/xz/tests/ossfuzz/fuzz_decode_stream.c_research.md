# sources/compression/xz/tests/ossfuzz/fuzz_decode_stream.c

Purpose: OSS-Fuzz target for single-threaded `.xz` stream decoding.

Important API: `LLVMFuzzerTestOneInput()` initializes `lzma_stream_decoder(&strm, MEM_LIMIT, flags)` and delegates execution to `fuzz_code()`. The flags include concatenated-stream handling and, when built for fuzzing, options that can relax checksum work to improve fuzz throughput.

Control flow: malformed inputs are expected and simply drive liblzma to non-OK returns. Initialization errors are printed and abort. After fuzz execution, `lzma_end()` releases state.

State and persistence: per-call stream state only. No output is retained; decompressed data is discarded by the common helper.

Dependencies and integration: covers xz container parsing, stream headers/footers, blocks, indexes, checks, and filter initialization reachable through the public decoder.

Risks: fuzzing with reduced check behavior can miss checksum-specific bugs, but it expands structural coverage. The 300 MiB limit bounds adversarial dictionary sizes.

Test signals: crashes, sanitizer reports, and unexpected `LZMA_PROG_ERROR` aborts. It complements deterministic tests like `test_files.sh`, `test_stream_flags.c`, and `test_index.c`.
