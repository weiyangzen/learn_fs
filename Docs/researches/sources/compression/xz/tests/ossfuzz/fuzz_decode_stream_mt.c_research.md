# sources/compression/xz/tests/ossfuzz/fuzz_decode_stream_mt.c

Purpose: OSS-Fuzz target for multithread-capable `.xz` stream decoding through `lzma_stream_decoder_mt()`.

Important API and configuration: `LLVMFuzzerTestOneInput()` sets up an `lzma_mt` struct with bounded threading and stop memory limits derived from `MEM_LIMIT`, initializes `lzma_stream_decoder_mt()`, runs `fuzz_code()`, and ends the stream.

Control flow: like the single-threaded stream fuzzer, it accepts arbitrary decode errors but aborts on initialization failure or `LZMA_PROG_ERROR`. The common helper feeds input in partial chunks and switches to `LZMA_FINISH` at the end.

State and persistence: per-iteration decoder/threading state only. No persistent state or output files.

Dependencies and integration: exercises threaded decoder paths, block scheduling, and memory-limit behavior that deterministic tests also touch in `test_check.c` and `test_memlimit.c`.

Risks: actual concurrency behavior depends on liblzma build options and OSS-Fuzz runtime. Memory limits are split between threading and stop conditions; setting them too low would reduce state coverage.

Test signals: thread sanitizer and address sanitizer reports are especially useful here, along with explicit aborts on program errors.
