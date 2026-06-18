# sources/compression/xz/tests/test_check.c

Purpose: tests integrity check APIs and decoder check-reporting behavior for `.xz` streams.

Important data and functions: EBCDIC-safe byte arrays for `"123456789"` vectors, generated random buffers, fixture pointers for no-check, unsupported-check, CRC32, CRC64, and SHA-256 streams. Tests include `test_lzma_crc32()`, `test_lzma_crc64()`, `test_lzma_supported_checks()`, `test_lzma_check_size()`, `test_lzma_get_check_st()`, and `test_lzma_get_check_mt()`.

Control flow: CRC tests verify standard vectors, unaligned input, incremental byte-at-a-time updates, and varied buffer alignments. Supported-check tests compare enabled compile-time features to `lzma_check_is_supported()`. Decoder tests initialize single-threaded or multithreaded decoders with `LZMA_TELL_ANY_CHECK`, `LZMA_TELL_UNSUPPORTED_CHECK`, and `LZMA_TELL_NO_CHECK`, then assert `LZMA_NO_CHECK`, `LZMA_UNSUPPORTED_CHECK`, or `LZMA_GET_CHECK` before `LZMA_STREAM_END`.

State and persistence: fixture data is loaded into process memory. Threaded decoder options carry memlimits but no persistent state.

Dependencies and integration: depends on liblzma check APIs, stream decoders, optional `MYTHREAD_ENABLED`, and fixture files in `tests/files`.

Risks: check availability is build-config-dependent, so assertions are guarded by macros. The tests deliberately avoid text literals for cross-character-set portability.

Test signals: detects CRC implementation regressions, check-size table drift, unsupported-check reporting bugs, and parity issues between single-threaded and threaded decoders.
