# sources/compression/xz/tests/test_memlimit.c

Purpose: tests decoder memory-limit errors and recovery for `.xz`, threaded `.xz`, `.lzma` alone, and auto decoders.

Important constants and state: `MEMLIMIT_TOO_LOW` is 1234 bytes; `MEMLIMIT_HIGH_ENOUGH` is 2 MiB; `in`/`in_size` hold a known-good `.xz` fixture; `out` is an 8192-byte decode buffer.

Control flow: each decoder is initialized with too-low memory, fed a complete known-good stream, and expected to return `LZMA_MEMLIMIT_ERROR`. The test asserts `lzma_memlimit_get()`, verifies a tiny increase still fails, then raises to a high-enough limit and expects `LZMA_STREAM_END`. Separate functions cover `lzma_stream_decoder()`, `lzma_stream_decoder_mt()`, `lzma_alone_decoder()`, and `lzma_auto_decoder()`.

State and persistence: decoder state is reset per function and freed with `lzma_end()`. Fixtures are memory-loaded only.

Dependencies and integration: uses `tests.h`, `mythread.h`, fixture files, and memory-limit APIs. Threaded test skips if `MYTHREAD_ENABLED` is absent.

Risks: recovery after memlimit failure is subtle because decoder state must preserve enough context to continue after the limit is raised. Minimal builds skip relevant paths.

Test signals: explicitly references a historical stream-decoder recovery bug fixed after liblzma 5.2.6/5.3.3alpha.
