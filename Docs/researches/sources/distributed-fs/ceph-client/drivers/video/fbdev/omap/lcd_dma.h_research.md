# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap/lcd_dma.h

## Purpose
`lcd_dma.h` defines OMAP1510/OMAP1610 LCD DMA register addresses, LCD DMA block identifiers, and the exported LCD DMA helper API used by the OMAP1 fbdev controller stack.

## Important APIs, Types, And Functions
- Register macros cover OMAP1510 LCD control/top/bottom registers and OMAP1610 LCD CSDP/CCR/CTRL/top/bottom/source-index/lch-control registers.
- The enum identifies the four OMAP1610 LCD DMA block slots: B1 top/bottom and B2 top/bottom.
- Function declarations expose reservation, setup, enable/stop, external-controller and single-transfer mode, B1 geometry, rotation, virtual stride, mirror, and scaling.

## Control Flow
The header has no executable flow. It establishes the contract used by `lcdc.c`, `sossi.c`, and any other legacy OMAP1 LCD DMA client.

## State And Persistence
No state is defined here. State lives in `lcd_dma.c`.

## Dependencies And Integration Points
This header is tightly coupled to OMAP1 physical register layout and to `linux/omap-dma.h` data-type constants used by callers.

## Risks
The hard-coded physical addresses make the API OMAP1-specific. Callers must respect unsupported OMAP1510 transform constraints enforced in the implementation. There is no type-safe geometry object, so callers can mix pixel and DMA-element dimensions incorrectly.

## Test Signals
Compile-time coverage is the main signal: all legacy OMAP LCDC and SoSSI code should build against these declarations without duplicate register definitions.
