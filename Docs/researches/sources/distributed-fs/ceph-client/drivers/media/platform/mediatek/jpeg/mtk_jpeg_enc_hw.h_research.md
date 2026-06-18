# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.h

## Purpose
This header defines JPEG encoder register offsets, control bits, quality codes, and exported hardware programming functions for the MediaTek JPEG encoder.

## Important APIs, Types, and Functions
Important macros include interrupt status bits, destination byte-offset mask, control bits for enable/interrupt/file-format/restart/YUV format, reset bit, hardware YUV format encodings, quality-code constants, and MMIO offsets from `JPEG_ENC_RSTB` through 34-bit address extension registers. `struct mtk_jpeg_enc_qlt` maps a public quality value to a hardware code. The exported functions reset, start, compute file size, and program source, destination, and encode parameters.

## Control Flow
The core includes this header to call the encoder setup sequence before starting hardware. The IRQ path also uses the file-size helper to set the captured JPEG payload.

## State and Persistence
The header has no runtime state. It defines the volatile register contract and the small immutable quality mapping element type.

## Dependencies and Integration Points
It includes videobuf2 core and `mtk_jpeg_core.h`, tying encoder programming to V4L2 buffer/context state. Register definitions are consumed only by the encoder implementation.

## Risks and Edge Cases
Macro drift from hardware documentation can silently break encoding. The `JEPG_ENC_YUV_FORMAT_NV21` spelling is typoed but still usable as a macro name if referenced. The register interface assumes callers provide correctly aligned DMA addresses and format-compatible context fields.

## Test Signals
Compile coverage, register trace checks, quality/format matrix encode tests, and 34-bit DMA tests validate this header indirectly.
