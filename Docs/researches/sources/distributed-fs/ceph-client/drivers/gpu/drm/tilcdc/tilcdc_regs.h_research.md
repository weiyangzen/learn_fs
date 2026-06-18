# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_regs.h

## Purpose

`tilcdc_regs.h` defines TI LCDC register offsets, status/control bit masks, DMA/timing/raster field helpers, and inline MMIO access helpers for the tilcdc driver.

## Important APIs, Types, and Definitions

- Status bits include EOF0/EOF1, palette load done, FIFO underflow, sync lost, and frame done.
- DMA control macros encode burst size, FIFO threshold, EOF interrupts, and dual-framebuffer enable.
- Control/raster/timing macros encode clock divisor, raster mode, palette load mode, TFT/monochrome flags, rev1/rev2 interrupt enables, rev2 clock enables, 24bpp unpack/mode, AC bias, sync edge, pixel clock inversion, HSYNC/VSYNC inversion, and LPP high bit.
- Register offsets cover PID, CTRL, STAT, RASTER timing/control, DMA framebuffer base/ceiling, rev2 IRQ status/enable/end-of-int, and clock reset/enable.
- Inline helpers `tilcdc_write()`, `tilcdc_write64()`, `tilcdc_read()`, `tilcdc_write_mask()`, `tilcdc_set()`, `tilcdc_clear()`, `tilcdc_irqstatus_reg()`, `tilcdc_read_irqstatus()`, and `tilcdc_clear_irqstatus()` centralize MMIO access.

## Control Flow

All tilcdc modules use these helpers to access registers through `struct tilcdc_drm_private::mmio`. Revision-dependent IRQ status selection is handled by `tilcdc_irqstatus_reg()`: rev2 uses `LCDC_MASKED_STAT_REG`, rev1 uses `LCDC_STAT_REG`.

## State and Persistence Behavior

The header has no state; it reads private MMIO state from the DRM device. Hardware register state persists until overwritten, reset, or PM loss. The 64-bit write helper attempts atomic base/ceiling programming where supported and falls back to an architecture-specific volatile 64-bit store.

## Dependencies and Integration Points

It includes Linux bitops and `tilcdc_drv.h`, and is consumed by CRTC, driver, and IRQ paths. It is tightly coupled to LCDC rev1/rev2 hardware behavior.

## Risks and Edge Cases

- `tilcdc_write64()` fallback uses a forced volatile 64-bit write and comments that it compiles to `strd` on ARM7; portability to other architectures requires care.
- Register masks use open-coded shifts in several callers; helper macros do not cover all fields.
- Rev2 interrupt disable must be done by writing clear registers in callers; the helpers only select status registers.
- Clearing IRQ status writes the supplied mask to the active status register, so callers must avoid clearing unobserved bits when that matters.

## Test Signals

Hardware tests should validate rev1/rev2 register dumps, 64-bit scanout address update behavior, IRQ status read/clear semantics, raster timing field programming, clock reset/enable bits, and endian correctness of DMA address writes.
