
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-regs.h

## Purpose

`c3-isp-regs.h` is the register map and bitfield macro header for the Amlogic C3 ISP driver. It defines offsets, masks, and value-construction macros used by the core, parameter, resizer, stats, and capture paths to program ISP top-level routing, processing blocks, display/scaler blocks, statistics engines, writeback MIF, and statistics DMA.

## Important APIs, Types, And Functions

The header exports preprocessor constants only. Key groups are `ISP_TOP_*` for input/core sizes, path enable/select, display input select, IRQ enable/clear/status, and feature enable bits; `ISP_LSWB_*` for BLC/WB offsets, gains, limits, and phase offsets; `ISP_DMS_*` for demosaic phase; `ISP_CM0_*`, `ISP_CCM_*`, and `ISP_PST_GAMMA_*` for color conversion, color correction, and gamma; `DISP0_*` and `ISP_SCALE0_*` for per-resizer crop/output/PPS scaler setup; `ISP_AF_*`, `ISP_AE_*`, and `ISP_AWB_*` for 3A stat block windows, coordinates, weights, and controls; `ISP_WRMIFX3_0_*` for capture writeback; and `VIU_DMAWR_*` for statistics DMA base/size.

Value macros use standard kernel helpers such as `BIT()` and `GENMASK()`, and often encode hardware-specific units, for example base addresses shifted by four bytes and size fields stored in 16-byte units by caller convention.

## Control Flow

There is no executable control flow. Runtime flow is embodied by users: `c3-isp-core.c` writes top sizes, path selection, IRQ masks, and phase offsets; `c3-isp-params.c` updates image-processing and statistics control fields; `c3-isp-resizer.c` applies display/scaler register offsets through `C3_ISP_DISP_REG()` in its own file; stats/capture code programs DMA address, size, and writeback format registers.

## State And Persistence

The file defines the symbolic contract for volatile MMIO state. It has no variables or persistent state. Correctness depends on macros matching silicon register layout and field widths.

## Dependencies And Integration Points

Every C3 ISP source file that touches hardware includes this header. It integrates with Linux bitfield idioms but mostly uses simple shift macros rather than `FIELD_PREP()`. The register names align with the ISP functional blocks visible in the media pipeline: input/core, resizer/display, writeback, 3A stats, and DMA.

## Risks

Many value macros do not mask their input before shifting, so callers must clamp and validate widths, heights, coordinates, gains, and matrix coefficients. Some constants encode zero values as `(0 << n)`, which is clear but offers no runtime protection against stale bits unless used with the correct mask in `c3_isp_update_bits()`. Address macros such as `ISP_WRMIFX3_0_CH0_BASE_ADDR(x)` and `VIU_DMAWR_*_BASE_ADDR(x)` shift DMA addresses right by four and assume suitable alignment. Register offset or mask drift from hardware documentation would create silent corruption across multiple modules.

## Test Signals

Compile with `W=1` to catch macro type/overflow warnings in call sites. Hardware bring-up should compare register dumps against expected values after each pipeline operation: core format setup, AWB/AE/AF config, gamma/CCM/CSC programming, resizer scaling, writeback format, and stats DMA. Static review should verify every value macro is paired with the intended mask and that callers clamp to field width before shifting.
