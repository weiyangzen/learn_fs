# sources/compression/xz/src/liblzma/common/vli_decoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_decoder.c -->
## sources/compression/xz/src/liblzma/common/vli_decoder.c

### Purpose
`vli_decoder.c` decodes liblzma variable-length integers from byte buffers, supporting both single-call and incremental decoding.

### Important APIs, Types, And Functions
The exported `lzma_vli_decode()` updates `*vli`, `*vli_pos`, and `*in_pos` while returning `LZMA_OK`, `LZMA_STREAM_END`, `LZMA_DATA_ERROR`, `LZMA_BUF_ERROR`, or `LZMA_PROG_ERROR` depending on mode and progress.

### Control Flow
With `vli_pos == NULL`, the function enters single-call mode, initializes a local position and `*vli`, and treats empty input as data error. In incremental mode, it initializes `*vli` only at byte position zero and validates that partial state is sane. It consumes bytes, adds seven-bit payloads at `7 * position`, stops on a byte without the continuation bit, rejects non-minimal encodings such as trailing zero payload in multibyte values, and rejects integers that exceed `LZMA_VLI_BYTES_MAX`.

### State, Persistence, And Dependencies
Incremental state is held by caller-owned `*vli` and `*vli_pos`. There is no internal persistence. The file depends on VLI constants and common return codes.

### Integration Points
Index, Block Header, filter flags, and other format decoders use this function to parse `.xz` integers from bounded buffers or streaming input.

### Risks
Callers must preserve `*vli` and `*vli_pos` exactly between incremental calls. Single-call and incremental modes intentionally differ on short input errors (`LZMA_DATA_ERROR` versus `LZMA_BUF_ERROR`/`LZMA_OK`), which tests and callers must account for.

### Test Signals
Tests should cover one-byte values, maximum VLI, overlong encodings, truncated single-call and incremental inputs, invalid partial state, and exact `in_pos` advancement.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_decoder.c -->
