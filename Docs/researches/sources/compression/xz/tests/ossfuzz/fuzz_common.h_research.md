# sources/compression/xz/tests/ossfuzz/fuzz_common.h

Purpose: shared helper code for liblzma OSS-Fuzz targets, especially chunked execution of `lzma_code()` with bounded memory.

Important constants and functions: `MEM_LIMIT` is 300 MiB to prevent pathological allocations from fuzzed headers. `IN_CHUNK_SIZE` is 2047 bytes. `fuzz_code(lzma_stream *, const uint8_t *, size_t)` feeds input through a prepared encoder or decoder and discards output into a 4096-byte stack buffer.

Control flow: `fuzz_code()` starts by giving half the input to the stream, then feeds remaining data in chunks. When input is exhausted it switches to `LZMA_FINISH`; when the output buffer fills it resets and overwrites it. The loop stops on any `lzma_code()` return other than `LZMA_OK`; `LZMA_PROG_ERROR` is treated as a target or library bug and aborts.

State and persistence: no persistent state. The function mutates the supplied `lzma_stream` and local input pointers only.

Dependencies and integration: included by decode and encode fuzz targets after they initialize the appropriate liblzma coder. Depends on `lzma.h`, stdint/inttypes, stdlib, and stdio.

Risks: the helper does not assert semantic success; it is designed to find crashes, memory errors, and illegal program-error returns. The unusual half-input first call improves state-machine coverage but must not be mistaken for normal streaming policy.

Test signals: fuzzer failures are crashes, sanitizer reports, or explicit abort on `LZMA_PROG_ERROR`.
