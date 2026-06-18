# sources/compression/xz/src/liblzma/api/lzma/vli.h

Purpose: declares `.xz` variable-length integer (VLI) limits, type, validation macro, and encode/decode/size APIs.

Important APIs/types/functions: defines `LZMA_VLI_MAX`, `LZMA_VLI_UNKNOWN`, `LZMA_VLI_BYTES_MAX`, `LZMA_VLI_C`, typedef `lzma_vli`, macro `lzma_vli_is_valid`, and functions `lzma_vli_encode`, `lzma_vli_decode`, `lzma_vli_size`.

Control flow: encode/decode support single-call mode when position pointer is NULL and multi-call mode when `vli_pos` tracks progress. Multi-call encode/decode returns `LZMA_OK` for incomplete progress and `LZMA_STREAM_END` when the integer is complete.

State and persistence: multi-call state is entirely caller-owned in `*vli_pos` and, for decode, partially accumulated in `*vli`. No heap or global state.

Dependencies/integration: VLI encodes filter IDs, property lengths, Block sizes, Index records, and Backward Size-related metadata. Most container, filter, block, and index APIs depend on its limits.

Risks: valid VLIs are limited to 63 bits; `UINT64_MAX` is reserved as unknown, not an encodable value. Non-minimal encodings are invalid. Single-call decode with truncated input returns `LZMA_DATA_ERROR`, while multi-call no-input returns `LZMA_BUF_ERROR`.

Test signals: VLI coverage appears through `tests/test_filter_flags.c`, Index tests, Block/Header tests, and any decoder tests with malformed size encodings.
