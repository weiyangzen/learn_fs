<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.h -->
# sources/compression/xz/src/liblzma/common/index.h

Purpose: Internal/test-facing header for Index constants and helper functions without pulling in the full `common.h` dependency tree.

Important APIs/macros: Defines `UNPADDED_SIZE_MIN`, `UNPADDED_SIZE_MAX`, `INDEX_INDICATOR`, declares `lzma_index_padding_size()` and `lzma_index_prealloc()`, and defines inline helpers `vli_ceil4()`, `index_size_unpadded()`, `index_size()`, and `index_stream_size()`.

Control flow/state: No runtime state. Helpers encode `.xz` Index layout rules: Index Indicator, record count, record list, CRC32, four-byte padding, and Stream Header/Footer overhead.

Dependencies/integration: This header intentionally assumes `lzma.h` or `common.h` was included first so include-order problems fail consistently. It is used by internal common files and tests.

Risks/tests: Size arithmetic must stay aligned with the `.xz` specification and encoder/decoder CRC/padding logic. Tests should assert known Index sizes, padding sizes, and VLI boundary behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.h -->
