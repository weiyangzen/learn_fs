# sources/distributed-fs/ceph-client/include/video/pxa168fb.h

## Purpose
`pxa168fb.h` defines platform data, pixel formats, pin modes, and private framebuffer state for Marvell PXA168 LCD controller support.

## Important APIs, Types, and Functions
Macros define dumb/smart interface pin modes, dumb RGB lane allocation modes, default framebuffer size, and packed/planar RGB/YUV/pseudocolor pixel format constants including `PIX_FMT_UYVY422PACK`. `struct pxa168fb_info` stores device, clock, fb_info, MMIO base, DMA framebuffer start, pseudo-palette, pixel format, blanked/rbswap/active flags. `struct pxa168fb_mach_info` carries platform id, mode list, default pixel format, pin allocation, dumb-mode lane routing, GPIO output mask/data, signal polarity flags, panel lane swap, active state, and enable flag.

## Control Flow
Platform code supplies `pxa168fb_mach_info`; the driver maps registers, enables the clock, allocates framebuffer memory, selects a mode and pixel format, programs pin allocation and dumb/smart panel routing, sets signal polarities and GPIO output bits, and tracks blank/active state in `pxa168fb_info`.

## State and Persistence Behavior
Runtime state is split between immutable or boot-time machine info and mutable framebuffer info. Hardware state includes LCD controller registers, pin mux/output state, DMA framebuffer base, blank/active state, and pseudo-palette. It persists for device lifetime and must be restored after suspend/resume.

## Dependencies and Integration Points
It depends on fbdev mode structures, interrupt declarations, devices, clocks, MMIO, and DMA addresses from including code. It integrates PXA168 board files/platform data with fbdev, panel wiring, LCD clocks, and scanout buffer management.

## Risks and Test Signals
Risks include mismatched pixel format names with MMP formats, lane-swap and RGB/BGR confusion, insufficient default framebuffer size for larger modes, polarity errors, and active/blank state divergence from hardware. Test signals include each supported panel wiring mode, RGB/YUV pixel formats, pseudo-palette updates, blank/unblank, suspend/resume, clock enable/disable, DMA base programming, and platform mode-list validation.
