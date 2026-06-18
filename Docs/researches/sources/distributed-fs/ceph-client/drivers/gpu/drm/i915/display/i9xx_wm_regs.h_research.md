# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm_regs.h

## Purpose

`i9xx_wm_regs.h` defines MMIO register addresses, field masks, shifts, register encoders, FIFO sizes, and maximum watermark constants used by the pre-SKL Intel display watermark code. It is a hardware-description header for legacy GMCH, Pineview, G4x, VLV/CHV, and Ironlake-style watermark programming.

## Important APIs, Types, And Macros

The header defines FIFO partition registers `DSPARB`, `DSPARB2`, `DSPARB3`, watermark registers `DSPFW1` through `DSPFW9_CHV`, high-order watermark registers `DSPHOWM`/`DSPHOWM1`, VLV drain latency registers `VLV_DDL(pipe)`, FIFO size constants such as `VALLEYVIEW_FIFO_SIZE`, `G4X_FIFO_SIZE`, `I965_FIFO_SIZE`, `I915_FIFO_SIZE`, and Pineview-specific limits. For Ironlake-style low-power watermarks it defines `WM0_PIPE_ILK(pipe)`, `WM1_LP_ILK`, `WM2_LP_ILK`, `WM3_LP_ILK`, `WM1S_LP_ILK`, `WM2S_LP_IVB`, `WM3S_LP_IVB`, `WM_MISC`, `WM_DBG`, and field macros such as `WM_LP_ENABLE`, `WM_LP_LATENCY()`, `WM_LP_PRIMARY()`, `WM_LP_CURSOR()`, and `WM_LP_SPRITE()`.

## Control Flow

This header has no runtime control flow. Consumers compose register values with the masks and `REG_FIELD_PREP` helpers before writing through `intel_de_write()` or read fields back through matching masks. The macros encode platform-specific register aliasing, such as Cherryview using `DSPFW7_CHV`, `DSPFW8_CHV`, and `DSPFW9_CHV` where some offsets overlap or differ from Valleyview.

## State And Persistence Behavior

No software state is stored here. The macros name hardware registers whose values persist until rewritten, reset, or lost through display power transitions. DSPARB fields persist FIFO boundaries; DSPFW and WM_LP fields persist plane, cursor, sprite, self-refresh, HPLL, and FBC watermark thresholds; VLV DDL fields persist drain latency settings.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PORT`, `_MMIO_BASE_PIPE3`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. It is consumed primarily by `i9xx_wm.c`, but its register names also document the hardware contract that readout and sanitize code must respect.

## Risks And Edge Cases

The main risk is mismatched masks and shifts, because many registers pack multiple planes and some VLV/CHV watermarks need high bits in separate registers. Comments noting unusual CHV offsets highlight hardware quirks that should not be normalized without checking the specification. Cursor masks differ from plane and sprite masks. The constants are in cachelines or register units, not bytes, so consumers must convert consistently.

## Test Signals

Signals include register read/write tracing during watermark programming, comparing generated bitfields against hardware documentation, VLV/CHV pipe A/B/C FIFO partition tests, G4x FBC/HPLL self-refresh tests, Ironlake LP watermark enable/disable sequences, and compile coverage after any register macro refactor.
