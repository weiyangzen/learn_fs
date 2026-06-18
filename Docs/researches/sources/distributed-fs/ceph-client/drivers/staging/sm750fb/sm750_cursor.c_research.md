## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_cursor.c

Purpose: this file implements hardware cursor programming for SM750-family devices. It controls cursor enable, position, colors, and conversion of fbdev 1-bpp cursor data into the hardware cursor memory format.

Important functions: `sm750_hw_cursor_enable()` writes the cursor image offset and enable bit; `sm750_hw_cursor_disable()` clears the cursor address register; `sm750_hw_cursor_set_size()` updates software width/height; `sm750_hw_cursor_set_pos()` writes the location register; `sm750_hw_cursor_set_color()` writes RGB565 foreground/background colors; `sm750_hw_cursor_set_data()` and `sm750_hw_cursor_set_data2()` pack color/mask bitmaps into 2-bit hardware cursor entries in IO memory.

Control flow: `sm750.c` configures each cursor's MMIO base to the channel-specific cursor block and places cursor image memory near the end of the CRTC video-memory allocation. Fbdev cursor updates disable the cursor, optionally update size, position, color map, and shape/image, then re-enable it if requested. Data packing loops over source bytes, computes 2-bit pixel codes, writes 16-bit units to cursor memory, and advances to a hardware row stride based on maximum cursor width.

State and persistence: cursor state is split between `struct lynx_cursor` fields (`w`, `h`, `vstart`, `offset`, `mmio`) and hardware cursor registers/image memory. Position and color persist in MMIO registers until changed or hardware reset.

Dependencies and integration points: called by `lynxfb_ops_cursor()` in `sm750.c`. It uses `struct lynx_cursor` from `sm750.h`, Linux IO accessors, fbdev ROP values, and local cursor register offsets that mirror panel/CRT cursor register layouts.

Risks: `sm750_hw_cursor_set_pos()` masks negative x/y values without setting the documented left/top sign bits, so off-screen cursor positioning may be wrong. `sm750_hw_cursor_set_data2()` advances rows when `!(i & (pitch - 1))`, which also triggers at `i == 0` and appears inconsistent with `set_data()`. Widths not divisible by 8 make `pitch = w >> 3` truncate. Cursor memory size is fixed from max dimensions, but source dimensions rely on prior validation in fbdev callback.

Test signals: hardware cursor movement near screen edges, negative positions, 1/8/16/64 pixel widths, ROP copy versus XOR shapes, color-map changes, dual-head cursor independence, and suspend/resume cursor memory clearing should be validated. Comparing set_data and set_data2 output can expose row-stride bugs.
