# sources/compression/xz/src/liblzma/common/stream_flags_common.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_common.c

### Purpose
`stream_flags_common.c` provides shared constants and comparison logic for `.xz` Stream Header/Footer flags. It centralizes the magic byte sequences and validates semantic consistency between decoded flags.

### Important APIs, Types, And Functions
It defines hidden `lzma_header_magic` and `lzma_footer_magic`. The exported `lzma_stream_flags_compare()` checks version, Check ID, Check equality, and optionally Backward Size equality when both values are known.

### Control Flow
Comparison accepts only version `0` structures. It rejects invalid Check IDs as programming errors, returns data error for Check mismatches, and compares Backward Size only when neither side is `LZMA_VLI_UNKNOWN`. Backward Size validation is delegated to `is_backward_size_valid()`.

### State, Persistence, And Dependencies
There is no mutable state. The constants are used by encoder and decoder files. Dependencies are the shared stream flags header, VLI constants, and public return codes.

### Integration Points
Decoded Stream Header/Footer pairs use this function to verify that a file's opening and closing flags match. It is also useful when comparing two Footers because known Backward Sizes are compared when available.

### Risks
The function intentionally treats unknown Backward Size as a wildcard, so callers that require Footer-to-Footer equality must ensure both sides have concrete values. Invalid caller-filled structures are reported as `LZMA_PROG_ERROR`, not data corruption.

### Test Signals
Tests should cover matching flags, Check mismatch, unknown versus known Backward Size, invalid Check IDs, invalid Backward Size alignment/range, and nonzero version rejection.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.c -->
