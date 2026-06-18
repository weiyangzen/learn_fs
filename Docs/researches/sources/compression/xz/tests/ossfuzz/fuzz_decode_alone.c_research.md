# sources/compression/xz/tests/ossfuzz/fuzz_decode_alone.c

Purpose: OSS-Fuzz target for legacy `.lzma` "alone" decoding through liblzma.

Important API: exposes `LLVMFuzzerTestOneInput(const uint8_t *, size_t)`. It initializes `lzma_stream` with `lzma_alone_decoder(&strm, MEM_LIMIT)`, passes the fuzzer input to `fuzz_code()`, then calls `lzma_end()`.

Control flow: initialization failures are considered unexpected except for extreme environment exhaustion, so the target prints the return code and aborts. Decode results other than `LZMA_PROG_ERROR` are allowed by `fuzz_code()` because malformed fuzz input is normal.

State and persistence: allocates decoder state inside `lzma_stream` and releases it every fuzz iteration. No persistent state exists.

Dependencies and integration: depends on `fuzz_common.h`, `lzma.h`, and OSS-Fuzz's `LLVMFuzzerTestOneInput` ABI. It exercises the `.lzma` decoder independently from `.xz` container parsing.

Risks: `MEM_LIMIT` must stay low enough for fuzzing infrastructure yet high enough to reach meaningful decoder states. Aborting on initialization failure may expose environment setup problems as crashes.

Test signals: sanitizer findings, crashes, and `LZMA_PROG_ERROR` aborts are meaningful. Successful fuzz cases return zero regardless of normal decode errors.
