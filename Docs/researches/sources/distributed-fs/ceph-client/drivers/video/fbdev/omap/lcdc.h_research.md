# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcdc.h

## Purpose
`lcdc.h` defines OMAP1 LCDC register addresses, status/control/IRQ bit masks, and the small callback API shared between the internal LCD controller and external interfaces.

## Important APIs, Types, And Functions
- Register macros define LCDC base, size, IRQ, and offsets for control, timing, status, subpanel, line interrupt, and display status.
- Status bits include DONE, VSYNC, SYNC_LOST, ABC, LINE_INT, FIFO underflow, and LOADED_PALETTE.
- Control/IRQ masks include LCD enable, TFT mode, IRQ mask fields, and DONE/VSYNC/line/palette interrupt bits.
- `omap_lcdc_set_dma_callback()` and `omap_lcdc_free_dma_callback()` let an external interface receive LCD DMA completion notification.
- `omap1_int_ctrl` is declared as the internal controller object.

## Control Flow
The header has no runtime control flow. It defines hardware constants and cross-file declarations used by `lcdc.c`, `lcd_dma.c`, and `sossi.c`.

## State And Persistence
No state is stored in this header.

## Dependencies And Integration Points
The header expects OMAP1 interrupt naming (`INT_LCD_CTRL`) and the `struct lcd_ctrl` type from `omapfb.h`.

## Risks
Hard-coded addresses and bit positions are OMAP1-specific. Any register definition drift would affect low-level DMA/controller behavior across multiple files.

## Test Signals
Compile coverage plus successful LCDC interrupt handling are the primary signals that these definitions match the target platform.
