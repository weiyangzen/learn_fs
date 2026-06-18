# File Research: sources/block-storage/kvdo/vdo/numeric.h

## Purpose
Provides inline little-endian encode/decode helpers for unaligned numeric fields.

## Key Helpers
- 64-bit signed/unsigned: `decode_int64_le`, `encode_int64_le`, `decode_uint64_le`, `encode_uint64_le`.
- 32-bit signed/unsigned: `decode_int32_le`, `encode_int32_le`, `decode_uint32_le`, `encode_uint32_le`.
- 16-bit unsigned: `decode_uint16_le`, `encode_uint16_le`.

## Behavior
Each decoder reads from `buffer + *offset`, stores the decoded value, and advances `*offset` by the type size. Each encoder writes to `data + *offset` and advances likewise.

## Integration Notes
Uses Linux unaligned little-endian primitives from `<asm/unaligned.h>`. Declares `numeric_compile_time_assertions()` as a compile-time type-size assertion hook.
