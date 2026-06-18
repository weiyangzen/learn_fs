# sources/compression/xz/tests/test_lzip_decoder.c

Purpose: tests liblzma's optional lzip decoder for v0/v1 files, concatenation, trailing data, checksum handling, malformed headers, and memlimit recovery.

Important helpers: `basic_lzip_decode()` decodes good fixtures one byte at a time and verifies output by CRC32. `trailing_helper()` decodes with `LZMA_CONCATENATED` and verifies trailing bytes remain readable. `decode_expect_error()` decodes bad fixtures and checks the expected `lzma_ret`.

Control flow: tests validate options errors, v0 and v1 decode, v0/v1 trailing behavior including magic-byte prefixes, concatenated member combinations, CRC error and `LZMA_IGNORE_CHECK`, `LZMA_TELL_ANY_CHECK`, invalid magic bytes, unsupported version, invalid dictionary size, invalid uncompressed/member sizes, and raising memlimit after `LZMA_MEMLIMIT_ERROR`.

State and persistence: loads fixture files into memory and uses stack output buffers. No files are written.

Dependencies and integration: gated by `HAVE_LZIP_DECODER`. Uses `lzma_lzip_decoder()`, `lzma_code()`, `lzma_memlimit_set()`, `lzma_get_check()`, fixture files, and CRC32.

Risks: lzip support is optional, so the entire file early-skips when disabled. CRCs are used instead of text comparisons for EBCDIC portability.

Test signals: covers both normal and adversarial lzip streams, with special attention to trailing input semantics and post-memlimit continuation.
