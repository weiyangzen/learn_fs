# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/numeric.h

## Purpose
`numeric.h` defines small inline helpers for little-endian integer serialization/deserialization from byte buffers while advancing an offset cursor.

## Important APIs, Types, and Functions
Helpers include `decode_s64_le()`, `encode_s64_le()`, `decode_u64_le()`, `encode_u64_le()`, `decode_s32_le()`, `encode_s32_le()`, `decode_u32_le()`, `encode_u32_le()`, `decode_u16_le()`, and `encode_u16_le()`.

## Control Flow
Each decode reads an unaligned little-endian integer at `buffer + *offset`, stores it to the output, and increments the offset by the type size. Each encode writes the value to `data + *offset` in little-endian order and increments the offset.

## State and Persistence Behavior
The only state mutation is the caller-provided offset cursor. The helpers are commonly used for persistent on-disk or wire-format structures where byte order must be fixed.

## Dependencies and Integration Points
It includes Linux unaligned, kernel, and type headers. It supports UDS/VDO encoders and decoders that need source-tree-local numeric helpers.

## Risks and Edge Cases
There is no bounds checking; callers must ensure the buffer has enough bytes. Signed helpers rely on storing through the corresponding unaligned unsigned access width. Offset pointer must be valid and initialized.

## Test Signals
Round-trip tests for each width/sign, unaligned buffer addresses, offset advancement, and known little-endian byte sequences validate behavior.
