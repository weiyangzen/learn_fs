# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa168fb.h

Purpose: defines the local PXA168/PXA910 LCD controller register offsets and bitfield helpers used by `pxa168fb.c`. It is a hardware register map rather than an exported API header.

Important APIs/types/functions: no functions or structs are defined. Key register groups include video DMA start/pitch/size registers, graphics start/pitch/position/size registers, hardware cursor registers, total and active timing registers, porch and blank color registers, color-key and alpha controls, SPI and smart-panel registers, DMA control registers, SRAM controls, clock divider, contrast/saturation/hue controls, dumb-panel control, IO pad control, interrupt enable/status registers, and mode constants. Format constants include `VMODE_*` and `GMODE_*`; dumb panel constants include `DUMB16_RGB565_*`, `DUMB18_RGB666_*`, `DUMB24_RGB888_0`, and `DUMB_BLANK`; IO pad modes include `IOPAD_DUMB*` and `IOPAD_SMART*`.

Control flow: the header contributes symbolic addresses and bit encoders to driver control flow. `pxa168fb.c` uses graphics registers for framebuffer base/pitch/size, `LCD_SPU_DMA_CTRL0/1` for format and trigger control, `LCD_SPU_DUMB_CTRL` for panel enable/blanking/polarity, `LCD_CFG_SCLK_DIV` for pixel clock division, `SPU_IOPAD_CONTROL` for platform pin muxing, and `SPU_IRQ_ENA`/`SPU_IRQ_ISR` for graphics-frame interrupt handling.

State and persistence: these macros describe persistent MMIO state in the LCD controller. They do not store kernel state themselves. Register fields persist in hardware until rewritten, reset, power loss, or driver removal. Palette SRAM writes are coordinated through `LCD_SPU_SRAM_WRDAT` and `LCD_SPU_SRAM_CTRL`.

Dependencies and integration: included only by the PXA168 fb driver in this set. It complements public platform data from `<video/pxa168fb.h>` and Linux `readl`/`writel` register access. Names are hardware-specific and not namespaced for generic reuse.

Risks: many masks and shifts are open-coded macros with no type checking. Some comments contain typos or historical naming ("Dump LCD Panel Control Register"), so readers must validate against silicon documentation. Duplicate or similar bit names for DMA/video/graphics paths make it easy to program the wrong plane. The header contains no compile-time field range checks; out-of-range arguments can bleed into neighboring fields.

Test signals: compile coverage through `pxa168fb.c` is the primary signal. Hardware tests should verify that each macro group used by the driver writes the expected register values for panel timing, pixel formats, palette mode, RGB swap, blanking, IO pad allocation, and IRQ enable/acknowledge. Static review should compare offsets and masks against the PXA168/PXA910 LCD controller reference manual.
