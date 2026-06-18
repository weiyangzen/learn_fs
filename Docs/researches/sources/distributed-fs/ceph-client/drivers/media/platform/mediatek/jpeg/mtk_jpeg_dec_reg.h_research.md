# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_reg.h

## Purpose
This header is the decoder register map for the MediaTek JPEG decode block. It names MMIO offsets, interrupt-status bits, and hardware constants consumed by `mtk_jpeg_dec_hw.c`.

## Important APIs, Types, and Functions
The file exports macros rather than functions. Important constants include `MTK_JPEG_BLOCK_MAX`, `MTK_JPEG_DCTSIZE`, interrupt masks such as `BIT_INQST_MASK_EOF` and `BIT_INQST_MASK_ALLIRQ`, base decoder control registers such as `JPGDEC_REG_RESET`, bitstream registers such as `JPGDEC_REG_FILE_ADDR`, output registers such as `JPGDEC_REG_DEST_ADDR0_Y`, and 34-bit extension registers.

## Control Flow
There is no executable control flow. The hardware helper composes register writes using these offsets during reset, configuration, trigger, and interrupt handling.

## State and Persistence
The macros describe volatile hardware state. Persistence is in the hardware register file only while the block is powered and configured.

## Dependencies and Integration Points
The header is included by `mtk_jpeg_dec_hw.h` and indirectly by parser/core users. The offsets must match the MediaTek JPEG decoder IP revision selected by device-tree compatibles.

## Risks and Edge Cases
Incorrect offsets or masks can corrupt unrelated decoder registers. The interrupt mask includes EOF, pause, underflow, overflow, and bitstream error but not every possible status bit, so new hardware status bits would need explicit handling. Extension-register use must stay aligned with platform 34-bit support.

## Test Signals
Register trace comparison against hardware documentation, IRQ status injection, and decode smoke tests on MT8195 are the main validation signals. Build tests catch only macro spelling, not semantic drift.
