<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c

Purpose: provides exported shared FBTFT bus helpers for writing controller registers and framebuffer memory over 8-, 9-, and 16-bit buses.

Important APIs/types/functions: macro `define_fbtft_write_reg()` generates and exports `fbtft_write_reg8_bus8()`, `fbtft_write_reg16_bus8()`, and `fbtft_write_reg16_bus16()`. `fbtft_write_reg8_bus9()` handles 9-bit command/data SPI, including 8-bit SPI emulation padding. Video-memory helpers are `fbtft_write_vmem16_bus8()`, `fbtft_write_vmem16_bus9()`, `fbtft_write_vmem8_bus8()` (stub), and `fbtft_write_vmem16_bus16()`.

Control flow: register helpers optionally log arguments, prepend `par->startbyte`, write the first argument with DC low as command, then write remaining arguments with DC high as data. Video-memory helpers set DC high and chunk framebuffer bytes through `par->txbuf` for endian conversion or 9-bit tagging. Non-buffered 16-over-8 writes fall back to raw `fbtftops.write()`.

State and persistence: no persistent state. It reads `struct fbtft_par` fields such as `buf`, `txbuf`, `startbyte`, `gpio.dc`, SPI bits-per-word, and framebuffer memory.

Dependencies and integration: exported to panel modules and used by FBTFT core defaults. Depends on GPIO descriptor DC control, SPI settings, endian helpers, and `fbtft_write_buf_dc()`.

Risks: the generated register helper's data write length multiplies by `sizeof(data_type) + offset`, which is subtle when `startbyte` is present. `fbtft_write_reg8_bus9()` pads when emulating 9-bit over 8-bit SPI and assumes zero is a no-op. `fbtft_write_vmem8_bus8()` is unimplemented and returns `-1`. All helpers assume valid buffers sized by the core.

Test signals: bus traces for command/data DC transitions, startbyte panels, 9-bit native and emulated SPI, endian correctness for RGB565, chunking across small tx buffers, null txbuf path, and callers accidentally selecting the unimplemented 8-bit vmem helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c -->
