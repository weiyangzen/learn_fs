# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.h

## Purpose
This header exposes the JPEG decode parser entry point to the MediaTek JPEG core.

## Important APIs, Types, and Functions
It forward-declares `struct mtk_jpeg_dec_param` through the included hardware header and declares `bool mtk_jpeg_parse(struct mtk_jpeg_dec_param *param, u8 *src_addr_va, u32 src_size)`.

## Control Flow
Callers pass a virtually mapped source buffer and its size. On success the provided decode parameter structure contains both parsed JPEG metadata and derived hardware layout.

## State and Persistence
No state is stored by the header. The caller owns the parameter object and source buffer lifetime.

## Dependencies and Integration Points
It includes `mtk_jpeg_dec_hw.h` because parsing is tied directly to decoder hardware parameter derivation. It is the bridge between bitstream parsing code and V4L2 decode scheduling.

## Risks and Edge Cases
The API does not expose detailed parse errors, so users only learn success or failure. Callers must ensure the source virtual address is valid for `src_size` bytes and remains mapped during parsing.

## Test Signals
Compile checks should verify the parser declaration stays in sync. Runtime decode setup should reject invalid JPEG headers by observing a false return from this API.
