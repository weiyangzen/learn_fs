# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_regs.h

## Purpose

`malidp_regs.h` is the register and bitfield definition header for Mali-DP500/DP550/DP650. It names interrupt bits, common display/scaling/memwrite fields, generic IRQ register offsets, timing-register offsets and pack macros, coefficient table registers, scaling-engine registers, memory-write registers, DP500-specific offsets, DP550/650 offsets, MMU control bits, and AFBC decoder registers.

## Important APIs, Types, And Macros

Important groups include `MALIDP*_DE_IRQ_*`, `MALIDP*_SE_IRQ_*`, `MALIDP*_DC_IRQ_*`, `MALIDP_CFG_VALID`, `MALIDP_DISP_FUNC_*`, `MALIDP_SCALE_ENGINE_EN`, `MALIDP_SE_MEMWRITE_EN`, `MALIDP_REG_STATUS/SETIRQ/MASKIRQ/CLEARIRQ`, timing pack macros such as `MALIDP_DE_H_FRONTPORCH()`, coefficient offsets, `MALIDP_SE_*` scaling/enhancer macros, `MALIDP_MW_*` registers, DP500/550 config/timing/layer/memwrite bases, `MALIDP_MMU_CTRL_*`, and AFBC decoder macros such as `MALIDP_AD_EN`, `MALIDP_AD_YTR`, and `MALIDP_AD_BS`.

## Control Flow

The header has no executable control flow. Driver code uses its constants to program variant-specific register maps through the callback tables in `malidp_hw.c`, plane programming in `malidp_planes.c`, writeback programming in `malidp_mw.c`, and commit/color/scaling programming in `malidp_drv.c`.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register state that persists in the display processor: IRQ masks/status, config-valid/mode bits, timing values, output depth, background color, coefficient tables, scaling state, memwrite DMA pointers, MMU prefetch control, and AFBC decoder state.

## Dependencies And Integration Points

The file depends only on C macros and bit definitions. It is consumed by `malidp_hw.h` and all Mali-DP implementation files. It encodes the differences between DP500's mixed register layout and the standardized DP550/650 layout.

## Risks And Edge Cases

DP500 and DP550/650 offsets are not interchangeable. Some registers are relative to block bases, while others are absolute variant offsets. IRQ clearing differs based on CLEARIRQ support outside this header. Timing macros mask values, so out-of-range values can be truncated unless earlier validation catches them. MMU prefetch page-size bits and AFBC crop/control bits must match format/modifier validation.

## Test Signals

Hardware smoke tests for each variant, register dumps before/after modeset, IRQ mask/status behavior, scaling/memwrite/AFBC functionality, interlaced timing programming, MMU prefetch tests, and static comparison against ARM register documentation are useful validation signals.
