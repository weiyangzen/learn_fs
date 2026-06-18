<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h -->
# sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h

Purpose: defines platform data and register/bit constants for the AT91/AT32 LCD Controller framebuffer driver.

Important APIs and types: `atmel_lcdfb_pdata` describes board-specific timing, backlight polarity, default bpp, LCD wiring mode, default control register values, power-control callback, default monitor specs, and power GPIO list. Register constants cover DMA frame buffers, LCD controller timing/configuration, FIFO, dither/palette, power, contrast PWM, interrupts, and LUT access. Bit masks encode DMA enable/update, display type, scan mode, interface width, pixel size, sync polarity, clocking, endianness, timing fields, and interrupt causes.

Control flow: board/platform code supplies pdata; the framebuffer driver programs DMA buffers, timing registers, pixel format, power/contrast, interrupts, and LUT entries using these constants during probe, mode set, blanking, and framebuffer updates.

State and persistence: runtime state lives in controller registers, DMA frame pointers, GPIO/backlight state, and framebuffer memory. Pdata is platform configuration rather than persistent kernel state.

Dependencies and integration points: depends on workqueue/list types and framebuffer monitor specs from surrounding includes. It integrates with Atmel platform devices, fbdev, board GPIO power control, DMA, and LCD panels.

Risks and test signals: risks include wrong bit masks/shifts, board wiring RGB/BGR mismatches, power sequencing via callbacks, DMA update races, and timing field limits. Test mode programming, blank/unblank, framebuffer pan/update, interrupt handling, RGB/BGR panels, and suspend/resume power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/atmel_lcdc.h -->
