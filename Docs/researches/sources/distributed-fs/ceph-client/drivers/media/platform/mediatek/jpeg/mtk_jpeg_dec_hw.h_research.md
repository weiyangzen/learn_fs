# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.h

## Purpose
This header defines the MediaTek JPEG decoder hardware ABI used between the parser/core and the hardware programming file. It exposes decoder result codes, decoded-frame parameter storage, bitstream/framebuffer DMA descriptors, and register-control function prototypes.

## Important APIs, Types, and Functions
`struct mtk_jpeg_dec_param` is the central decoded-frame description: picture size, output size/fourcc, component IDs, sampling factors, quantization-table IDs, MCU and DMA grouping, membership map, strides, component sizes, and UV downscale state. `struct mtk_jpeg_bs` describes input bitstream DMA start/end/size. `struct mtk_jpeg_fb` describes destination plane DMA addresses. Public APIs include fill, interrupt classification, reset/start, and full hardware configuration.

## Control Flow
JPEG marker parsing fills the raw SOF-derived fields, then `mtk_jpeg_dec_fill_param()` populates derived fields before `mtk_jpeg_dec_set_config()` consumes the same structure to program hardware. Interrupt handlers use the result enum returned by `mtk_jpeg_dec_enum_result()`.

## State and Persistence
The header defines in-memory job state only. The structures are per decode operation or per queued buffer and are not persistent storage. Their correctness controls hardware register state and V4L2 payload reporting.

## Dependencies and Integration Points
It includes videobuf2 core types and `mtk_jpeg_dec_reg.h`, and it is shared by parser, core scheduling code, and decode hardware implementation. `MTK_JPEG_COMP_MAX` fixes the decoder model to at most three JPEG components.

## Risks and Edge Cases
The structures do not encode validity ranges, so callers must prevent invalid component counts, zero dimensions, unsupported sampling factors, and insufficient destination planes. `size_t` and `dma_addr_t` fields are architecture-dependent and must match the register programming paths, especially with 34-bit address support.

## Test Signals
Compile coverage should catch prototype drift. Runtime tests should confirm all fields are filled before hardware programming, plane arrays are bounded by `MTK_JPEG_COMP_MAX`, and result-code mapping matches documented interrupt bits.
