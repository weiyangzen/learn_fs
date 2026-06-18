# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.h

## Purpose
Defines the Marvell MMP LCD controller register layout, bitfield macros, path helpers, DSI/LVDS register structures, and private hardware controller/path state used by `mmp_ctrl.c` and `mmp_spi.c`.

## Important APIs, Types, and Functions
- `struct lcd_regs` maps path-local video, graphics, cursor, timing, blanking, color key, and vsync registers.
- Macros such as `dma_ctrl()`, `intf_ctrl()`, `LCD_SCLK()`, `dma_fmt()`, `dma_mask()`, and interrupt mask helpers compose register offsets and bitfields for different paths.
- Register definitions cover graphics/video DMA, smart/dumb panel SPI, interrupts, SRAM, DSI, LVDS, I/O pad modes, alpha, dither, and timing-master controls.
- `enum { PATH_PN, PATH_TV, PATH_P2 }` identifies controller paths.
- `struct mmphw_path_plat` links an MMP core path to hardware-specific config.
- `struct mmphw_ctrl` stores controller-wide MMIO, clock, IRQ, and path-platform state.
- Inline helpers `overlay_is_vid()`, `path_to_ctrl()`, `ctrl_regs()`, and `path_regs()` translate public path/overlay objects into hardware register views.
- `lcd_spi_register()` is declared when SPI support is enabled.

## Control Flow
The header itself is declarative. Runtime code uses `path_regs()` to select the correct register block for PN, TV, or P2 paths and uses bit macros to update format, DMA, interrupts, clock, and interface settings.

## State and Persistence
No independent state, but it defines the state containers allocated by the controller driver and the layout of persistent hardware registers.

## Dependencies and Integration Points
Includes `<video/mmp_disp.h>` for public MMP display objects. It is the private integration contract between MMP hardware controller, SPI adapter, and any code touching LCD controller registers.

## Risks
This header is broad and hardware-specific; incorrect path IDs can trigger `BUG_ON(1)` in `path_regs()`. Numerous bitfield macros assume register semantics and path mappings. Some comments identify guessed or duplicated definitions, especially PN2 interrupt masks and DSI macro duplication. Because state structs are private, external code must go through the public MMP display API.

## Test Signals
Compile all MMP hardware and SPI configurations. Runtime validation includes correct register block selection for PN/TV/P2 paths, expected DMA format bits for each `PIXFMT_*`, interrupt mask composition, SPI register access, and DSI/LVDS builds even when not actively used.
