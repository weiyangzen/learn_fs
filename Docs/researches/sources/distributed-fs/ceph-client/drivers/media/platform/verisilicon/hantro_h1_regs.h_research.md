# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_h1_regs.h

## Purpose
Defines H1 encoder register offsets and bitfield macros, including common AXI/interrupt fields, JPEG mode controls, input image controls, stream limits, quantization table addresses, and additional H264/VP8-era encoder fields.

## Important APIs, Types, And Functions
This header is declarative. JPEG code uses `H1_REG_INTERRUPT`, `H1_REG_AXI_CTRL`, `H1_REG_ADDR_OUTPUT_STREAM`, `H1_REG_STR_BUF_LIMIT`, `H1_REG_ADDR_IN_PLANE_*`, `H1_REG_ENC_CTRL`, `H1_REG_IN_IMG_CTRL`, `H1_REG_JPEG_LUMA_QUAT(i)`, and `H1_REG_JPEG_CHROMA_QUAT(i)`.

## Control Flow And State
No runtime state is stored. The macros define how encoder backends compose register values and address offsets. Several definitions support codecs not in this work item, so changes affect a wider encoder surface.

## Dependencies And Integration Points
Included by H1 JPEG encode code and other H1 encoder paths. It assumes standard `BIT` style macros through includers.

## Risks And Test Signals
Contiguous quant-table register ordering is required by hardware and called out by the JPEG encoder. Regression signals include JPEG register traces, payload-size correctness, and compile coverage for other H1 encoder code that shares these definitions.
