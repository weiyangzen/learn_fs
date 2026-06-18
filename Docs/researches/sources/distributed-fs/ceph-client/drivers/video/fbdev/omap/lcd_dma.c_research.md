# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.c

## Purpose
`lcd_dma.c` implements OMAP1 LCD DMA setup and control helpers used by the legacy LCDC and external-controller paths. It configures framebuffer source addresses, rotation/mirroring/virtual stride/scaling transforms, and starts/stops the dedicated LCD DMA channel.

## Important APIs, Types, And Functions
- `struct lcd_dma_info lcd_dma` stores reservation state, callback, active flag, framebuffer geometry, transform parameters, external-controller mode, and single-transfer mode.
- Exported setters include `omap_set_lcd_dma_b1()`, `_rotation()`, `_mirror()`, `_vxres()`, `_scale()`, `_ext_controller()`, and `_single_transfer()`.
- `set_b1_regs()` computes top/bottom addresses, element/frame indexes, and register values for OMAP1510 or OMAP1610 LCD DMA.
- `omap_request_lcd_dma()` and `omap_free_lcd_dma()` reserve/release the singleton LCD DMA path.
- `omap_setup_lcd_dma()`, `omap_enable_lcd_dma()`, and `omap_stop_lcd_dma()` program and control the hardware.
- `lcd_dma_irq_handler()` acknowledges OMAP1610 block interrupts and invokes the registered callback.

## Control Flow
Clients reserve the LCD DMA channel, set framebuffer geometry and optional transforms, then call `omap_setup_lcd_dma()`. Setup writes reasonable OMAP1610 defaults, calls `set_b1_regs()`, and programs end-prog/autoinit/repeat bits unless single-transfer mode is active. Internal LCDC mode relies on controller enable to trigger transfers; external controller mode explicitly sets enable bits in `omap_enable_lcd_dma()`. The IRQ handler clears the block interrupt, marks DMA inactive, and calls the client callback.

## State And Persistence
All state is static and singleton. The driver records only the latest B1 plane parameters. The `reserved` flag is protected by a spinlock, but most geometry setters write without locking and assume serialized controller use.

## Dependencies And Integration Points
The file depends on OMAP1 CPU-detection helpers, OMAP DMA register definitions, OMAP1 IO accessors, LCDC register definitions, and `INT_DMA_LCD`. It is consumed by `lcdc.c` and external bus drivers such as `sossi.c`.

## Risks
Unsupported operations on OMAP1510 call `BUG()`. Address and stride math is sensitive to element size, rotation, mirror, virtual xres, and scaling; bad parameters can program invalid DMA windows. `omap_request_lcd_dma()` calls `BUG()` when already reserved, which turns a caller bug into a kernel crash. There is no locking around active state or most configuration fields, so callers must serialize setup and enable.

## Test Signals
Exercise RGB565/CLUT modes with no transform, mirror, and 90/180/270 rotation on OMAP1610. Confirm OMAP1510 rejects transforms, external mode receives DMA completion callbacks, and `omap_lcd_dma_running()` matches hardware state.
