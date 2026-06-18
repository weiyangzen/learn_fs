# sources/distributed-fs/ceph-client/drivers/video/console/newport_con.c

Purpose: SGI Newport/NG1 console driver for Indy GIO graphics hardware. It renders text directly through memory-mapped Newport registers and can display a boot logo.

Important APIs/types/functions: `newport_con` implements `struct consw`. `newport_probe()` binds a GIO device ID `0x7e`, maps registers, and calls `do_take_over_console()`. Rendering helpers include `newport_render_background()`, `newport_putc()`, `newport_putcs()`, `newport_clear_screen()`, `newport_scroll()`, and cursor/blank operations. Font management uses `font_data_t` references with `newport_set_font()` and `newport_set_def_font()`.

Control flow: startup validates register access, initializes default fonts, resets VC2/cmap/xmap state, reports revisions, derives screen size from VC2 timing tables, and returns the console name. Switch resets topscan and optionally draws a CLUT224 Linux logo. Drawing clears glyph background and writes z-pattern rows. Full-screen scrolling uses hardware topscan; partial scrolling redraws changed cells from the VC buffer.

State and persistence: globals hold mapped register pointer/address, screen size, topscan, logo state, init flag, cursor correction, and per-console font references. Hardware cmap/registers persist until reset/remove.

Dependencies and integration: SGI IP22 GIO bus, Newport register definitions, font and logo subsystems, VT console core, MMIO region ownership.

Risks: supports only one Newport console and assumes ioremap success in a comment. Logo state suppresses clears until scrolling disables it. Font support is limited to 8x16 with 256/512 chars. Tests need SGI hardware or MMIO emulation: probe/remove resource handling, register sanity failure, font refcount reuse, topscan scroll, logo activation, blanking, and partial-scroll redraw.
