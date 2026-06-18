# sources/compression/xz/tests/test_vli.c

Purpose: C unit test for liblzma variable-length integer helpers: `lzma_vli_size()`, `lzma_vli_encode()`, and `lzma_vli_decode()`.

Important APIs/functions: uses `lzma_vli_size`, `lzma_vli_encode`, `lzma_vli_decode`, `LZMA_VLI_MAX`, `LZMA_VLI_UNKNOWN`, `LZMA_VLI_BYTES_MAX`, `LZMA_OK`, `LZMA_STREAM_END`, `LZMA_BUF_ERROR`, `LZMA_DATA_ERROR`, and `LZMA_PROG_ERROR`. Test helpers `encode_single_call_mode`, `encode_multi_call_mode`, `decode_single_call_mode`, and `decode_multi_call_mode` compare against precomputed VLI byte sequences.

Control flow: `test_lzma_vli_size` verifies invalid values return zero and that encoded length increases every seven value bits. Encode tests first verify invalid inputs do not mutate positions or output, then cover all one- through nine-byte encodings in single-call and byte-by-byte multi-call modes. Decode tests cover empty input, malformed continuation bytes, invalid positions, and the same one- through nine-byte values in single- and multi-call modes.

State and persistence: in-memory only. It uses fixed arrays of expected bytes and stack output buffers.

Dependencies and integration: includes `tests.h`, which supplies liblzma headers and `tuktest` assertions. Compile-time feature macros gate encoder and decoder tests; missing support produces skipped subtests instead of compilation failures.

Risks: the test assumes the precomputed encoded values are authoritative; an error in those constants would enshrine incorrect behavior. It does not fuzz malformed encodings beyond a few boundary cases.

Test signals: `main` registers the three test functions with `tuktest`. Failures report enum names through `assert_lzma_ret`; skip behavior reflects disabled encoders/decoders.
