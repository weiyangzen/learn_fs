# sources/compression/xz/src/liblzma/common/vli_encoder.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_encoder.c -->
## sources/compression/xz/src/liblzma/common/vli_encoder.c

### Purpose
`vli_encoder.c` encodes liblzma variable-length integers, supporting both single-call output and incremental output across small buffers.

### Important APIs, Types, And Functions
The exported `lzma_vli_encode()` takes a `lzma_vli`, optional `vli_pos`, output buffer pointers, and returns completion or buffer/prog errors according to mode.

### Control Flow
Single-call mode uses a local position and expects sufficient output space. Incremental mode returns `LZMA_BUF_ERROR` if called with no output space. The function validates `vli_pos` and range, shifts away already-emitted seven-bit groups, writes continuation bytes while the remaining value is at least `0x80`, and writes a final byte without the high bit. Completion returns `LZMA_OK` in single-call mode and `LZMA_STREAM_END` in incremental mode.

### State, Persistence, And Dependencies
Incremental state is caller-owned `*vli_pos`; no state is retained internally. Dependencies are `common.h`, VLI constants, and output-position conventions.

### Integration Points
Format encoders use this for Index, Block Header, and filter property integer fields.

### Risks
Single-call callers that under-allocate output space get `LZMA_PROG_ERROR`, so size calculation via `lzma_vli_size()` is expected. Incremental callers must pass the same original VLI and preserved `vli_pos` on later calls.

### Test Signals
Tests should cover boundary values, maximum VLI, invalid values above maximum, exact-sized output, one-byte-at-a-time incremental output, and empty-output error behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_encoder.c -->
