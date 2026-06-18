# sources/compression/xz/tests/test_index_hash.c

Purpose: tests `lzma_index_hash`, the lightweight structure used to verify decoded Index records against expected block sizes.

Important helpers: `fill_index_hash()` appends expected records. `generate_index()` manually writes an `.xz` Index byte sequence: indicator, record count, VLI records, padding, and CRC32.

Control flow: init tests verify NULL creates a new hash and non-NULL reinitializes the same pointer. Append tests cover NULL hash, invalid unpadded/uncompressed sizes, successful records, and compressed-size overflow. Decode tests generate indexes for two, three, five, and six records; verify buffer-size errors, bad indicator, byte-at-a-time decode, mismatched unpadded sizes, corrupt CRC, and mismatched record content. Size tests assert expected encoded Index sizes for empty, one-record, two-record, and larger-VLI cases.

State and persistence: all data is heap memory owned by the test and `lzma_index_hash`. No files.

Dependencies and integration: includes internal `common/index.h` for `UNPADDED_SIZE_MIN`, `UNPADDED_SIZE_MAX`, `INDEX_INDICATOR`, `vli_ceil4()`, and index sizing semantics. Uses VLI and CRC public helpers.

Risks: manual Index generation must stay synchronized with the `.xz` specification. Encoder support is required for VLI generation in decode tests, even though `lzma_index_hash` itself is decoder-oriented.

Test signals: detects record-hash mismatches, streaming decode state bugs, padding/CRC validation problems, and size-accounting regressions.
