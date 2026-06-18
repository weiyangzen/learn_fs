# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_regs.h

## Purpose
Defines Rockchip VPU2 VEPU/VDPU register offsets and bitfield macros shared by Rockchip JPEG/VP8/H.264/MPEG-2 encoder and decoder code. It is a hardware map, not executable logic.

## Important APIs, Types, And Functions
- Provides VEPU encoder register macros for VP8 quantization/penalties, JPEG luma/chroma quant tables, input plane/output stream addresses, image stride/crop, H.264 controls, ROI, endian, interrupts, and encode start.
- Provides VDPU decoder register macros for common decode control, stream length, endian, interrupts, AXI, H.264 reference lists and controls, and VP8 partition/filter/segment/reference registers.
- Consumed by `rockchip_vpu2_hw_jpeg_enc.c`, `rockchip_vpu_hw.c`, and related Rockchip codec implementation files.

## Control Flow
There is no runtime control flow. Callers compose register values by ORing these macros and write them through `vepu_write*()`, `vdpu_write*()`, `hantro_reg_write()`, or `hantro_write_addr()`.

## State And Persistence
The header owns no state. Its definitions describe transient MMIO state in the VPU hardware blocks. Persistence and synchronization are handled by codec run functions and Hantro core locking/IRQ paths.

## Dependencies And Integration Points
Depends on Linux `BIT()` and bitfield conventions already visible through included compilation units. The register names align Rockchip-specific implementations with the generic Hantro codec-operation tables in `rockchip_vpu_hw.c`.

## Risks And Edge Cases
The file contains many overlapping offsets because different codecs reuse the same hardware register window; accidental cross-codec macro use can silently program the wrong field. A few macros reference `x` in the expansion while lacking an `(x)` parameter, which is a latent compile hazard if those macros are used. Hardware-specific ordering requirements, such as JPEG quant table block writes, are not enforceable by this header.

## Test Signals
Build all Rockchip Hantro variants with warnings enabled to catch bad macro use. Runtime validation comes from codec-level decode/encode tests and IRQ status checks on all supported VDPU2/VEPU2 SoCs.
