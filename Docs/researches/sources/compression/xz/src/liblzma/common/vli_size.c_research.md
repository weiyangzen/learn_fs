# sources/compression/xz/src/liblzma/common/vli_size.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_size.c -->
## sources/compression/xz/src/liblzma/common/vli_size.c

### Purpose
`vli_size.c` calculates how many bytes are needed to encode a liblzma variable-length integer.

### Important APIs, Types, And Functions
The exported `lzma_vli_size()` returns a byte count from 1 through `LZMA_VLI_BYTES_MAX`, or `0` for values above `LZMA_VLI_MAX`.

### Control Flow
The function rejects out-of-range values, then repeatedly shifts by seven bits until the value becomes zero, counting emitted groups.

### State, Persistence, And Dependencies
There is no state. It depends on VLI constants from `common.h`.

### Integration Points
Encoders use this to size headers, Index fields, and buffers before calling `lzma_vli_encode()`.

### Risks
Returning zero is the only error signal. Callers must not confuse it with a valid size, because every valid VLI uses at least one byte.

### Test Signals
Tests should check 0, 127, 128, every 7-bit boundary, `LZMA_VLI_MAX`, and `LZMA_VLI_MAX + 1`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_size.c -->
