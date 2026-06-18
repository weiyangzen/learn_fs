# sources/compression/xz/tests/test_block_header.c

Purpose: validates liblzma Block Header sizing, encoding, and decoding for `.xz` Blocks.

Important helpers and data: global `opt_lzma`, filter chains with zero, one, four, and five filters, and `RESET_BLOCK()` for clearing decoded state while preserving allocated filter arrays. `compare_blocks()` compares key `lzma_block` fields and filter IDs.

Control flow: `test_lzma_block_header_size()` checks valid size ranges, invalid version/size/filter cases, and cases intentionally ignored by size calculation. `test_lzma_block_header_encode()` validates bad header sizes, bad block fields, invalid filters, and exact encoded bytes including flags, VLI filter ID/property size, padding, and CRC32. `test_lzma_block_header_decode()` round-trips simple and multi-filter headers, validates decoder version adjustment, then corrupts check type, CRC, padding, and flags to assert correct errors.

State and persistence: stack buffers hold encoded headers. Decoded filters allocate option memory that is freed with `lzma_filters_free()`.

Dependencies and integration: uses liblzma block, filter, VLI, property, and CRC APIs. Requires x86 BCJ support for multi-filter tests and LZMA preset initialization in `main()`.

Risks: Block Headers are compact binary contracts; off-by-one header size, bad padding, or missing CRC validation can corrupt downstream decoding. Some option validation is intentionally deferred outside header-size calculation.

Test signals: strong byte-level checks and corruption tests. Skips on missing encoder/decoder/filter support.
