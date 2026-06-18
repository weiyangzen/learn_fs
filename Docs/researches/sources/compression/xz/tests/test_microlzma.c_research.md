# sources/compression/xz/tests/test_microlzma.c

Purpose: tests MicroLZMA encoder and decoder APIs, including option validation, exact compressed/uncompressed-size handling, action constraints, and property-byte behavior.

Important helpers and data: `BUFFER_SIZE`, `ENCODED_OUTPUT_SIZE`, `hello_world`, expected encoded CRC, local `lzma_lzma_lclppb_decode()` for verifying MicroLZMA property-byte negation, `goodbye_world`, generated `goodbye_world_encoded`, and `basic_microlzma_encode()`.

Control flow: encoder tests validate NULL stream, invalid lc/lp/pb combinations, dictionary limits, basic encode output and property byte, too-small output buffers, and unsupported actions other than `LZMA_FINISH`. Decoder tests, when both LZMA1 encoder and decoder exist, verify correct size decode with exact and inexact modes, too-large and too-small uncompressed sizes, wrong compressed size behavior, invalid LZMA properties, and valid-but-wrong properties leading to data errors.

State and persistence: encoded data is heap-allocated for decoder tests and stored in globals. No files are used.

Dependencies and integration: gated by `HAVE_ENCODER_LZMA1` and `HAVE_DECODER_LZMA1`. Uses MicroLZMA public APIs, LZMA presets, CRC32, and tuktest.

Risks: exact-size semantics are nuanced; one FIXME notes a case where repeated `LZMA_FINISH` eventually returns `LZMA_BUF_ERROR` instead of an immediate data error. The expected encoded CRC locks output stability and may need deliberate updates if encoder tuning changes.

Test signals: catches MicroLZMA regression in output format, unsupported action handling, size-boundary errors, and property validation.
