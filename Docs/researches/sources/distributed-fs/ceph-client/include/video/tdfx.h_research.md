<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tdfx.h -->
# sources/distributed-fs/ceph-client/include/video/tdfx.h

## Purpose
This header defines 3Dfx Banshee/Voodoo3-style framebuffer register offsets, bit masks, I2C/DDC bit positions, VGA port constants, and kernel-private driver state.

## Important APIs, Types, And Functions
- Register offsets cover `membase0` init, PLL, DAC, video processor, cursor, overlay, 2D engine, and 3D command spaces.
- Bit masks cover 2D ROP/commands, busy/retrace status, CLUT behavior, memory type, VGA disable/extended timing, video processor enable, cursor enable, pixel format, and DAC 2x mode.
- DDC/I2C masks in `VIDSERPARPORT` drive bit-banged monitor probing.
- `struct banshee_reg` stores VGA and extension registers for save/restore.
- `struct tdfxfb_i2c_chan` wraps an I2C adapter and bit-bang algorithm data.
- `struct tdfx_par` stores max pixel clock, pseudo palette, mapped registers, I/O base, write-combine cookie, and optional I2C channels.

## Control Flow
Driver flow maps registers, saves/restores VGA/Banshee state, computes PLLs, programs screen size/stride/video processor, controls hardware cursor, uses 2D command registers for fill/blit, and optionally bit-bangs DDC/I2C over `VIDSERPARPORT`.

## State And Persistence
State lives in `tdfx_par`, saved `banshee_reg`, MMIO registers, VGA legacy ports, CLUT/palette, write-combine mapping, and optional I2C adapters. Hardware state persists across driver operations until reset or restored.

## Dependencies And Integration Points
It depends on Linux I2C and i2c-algo-bit when `CONFIG_FB_3DFX_I2C` is enabled, fbdev driver code, VGA register access, MMIO, and PCI resource setup.

## Risks And Edge Cases
Legacy VGA constants are explicitly not multihead-safe. Incorrect write-combine handling can corrupt framebuffer access. 2D command launch must respect `STATUS_BUSY`. I2C bit masks share one serial port register and need careful direction/value handling.

## Test Signals
Signals include mode set and restore, DDC reads on both optional channels, correct cursor and palette behavior, 2D fill/blit completion, no busy timeouts, and clean suspend/resume of saved VGA/extension registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tdfx.h -->
