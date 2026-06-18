
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_dvt.c

Purpose: provides discrete, table-driven video timings for i810 when VESA GTF support is not selected. It maps supported resolutions/refreshes to complete VGA, PLL, watermark, and sync register values.

Important APIs and data: `std_modes[]` is the core table of `struct mode_registers` values for 640x480 through 1600x1200 at selected refresh rates. `round_off_xres()` clamps requested horizontal resolution to supported buckets. `round_off_yres()` derives 4:3 vertical resolution. `i810fb_find_best_mode()` chooses a table row by horizontal display register and nearest pixel clock not exceeding the request. `i810fb_encode_registers()`, `i810fb_fill_var_timings()`, and `i810_get_watermark()` are consumed by `i810_main.c`.

Control flow: check-var first rounds modes, then `i810fb_fill_var_timings()` converts the selected table entry back into fb_var margins, sync length, pixclock, and sync polarity. Set-par later calls `i810fb_encode_registers()` to copy the chosen table entry into `par->regs` and compute overlay active extents. Watermark selection is a simple lookup from the chosen table entry by memory frequency and bpp.

State and persistence: no dynamic storage is owned here. The file writes into `fb_var_screeninfo` and `i810fb_par->regs`, `ovract`, and watermarks selected elsewhere.

Dependencies and integration: depends on `i810.h` for `struct mode_registers` and `struct i810fb_par`, on `i810_regs.h` for register semantics, and on the main driver for validation, PLL programming, and register load.

Risks: supported modes are limited to table entries and 4:3 rounding, so unusual panels and custom timings are rejected or silently coerced. `i810fb_find_best_mode()` leaves `diff` unchanged for entries above the requested pixel clock, so selection behavior depends on table ordering. Sync polarity code uses bitwise complement tests that are easy to misread and should be regression tested.

Test signals: verify each supported mode round-trips from var to register table and back, check memory-frequency watermark selection for 100 and 133 MHz paths, and validate fallback behavior for requests between supported resolutions or refreshes.
