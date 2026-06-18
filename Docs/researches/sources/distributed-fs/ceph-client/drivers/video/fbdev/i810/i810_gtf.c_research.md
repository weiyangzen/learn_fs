
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_gtf.c

Purpose: implements non-discrete timing generation for i810 when `CONFIG_FB_I810_GTF` is enabled. Unlike `i810_dvt.c`, this file computes CRT/VGA register fields from fbdev timing values and uses separate FIFO watermark tables.

Important APIs and data: watermark tables `i810_wm_*_{100,133}` map pixel frequencies to FIFO control values for 8/16/24 bpp at 100 or 133 MHz memory. `round_off_xres()` and `round_off_yres()` are no-ops in GTF mode, leaving mode selection to fbdev modelist/GTF validation. `i810fb_encode_registers()` converts `fb_var_screeninfo` into CRTC, sync, blanking, interlace, double-scan, polarity, and overlay registers. `i810_get_watermark()` picks the nearest frequency entry.

Control flow: main check-var validates or synthesizes fb_var timings, then `decode_var()` calls `i810_calc_dclk()` in `i810_main.c`, followed by this file's `i810fb_encode_registers()`. Horizontal values are rounded to character clocks, blanking windows are constrained to 127-character ranges, vertical extension registers carry high bits, and sync polarity is encoded in `msr`.

State and persistence: stores derived state into `par->regs`, `par->interlace`, `par->ovract`, and later `par->watermark`. It reads the existing `CR11` register to preserve protected bits while writing the vertical retrace end low bits.

Dependencies and integration: depends on i810 MMIO read helpers, fbdev timing validation, and the main driver's later `i810_load_*()` register programming. It is selected mutually with DVT through `CONFIG_FB_I810_GTF`.

Risks: hardware register packing is dense and relies on valid, range-checked fb_var values. Division by very small pixclock values is protected by higher-level validation, not here. The nearest watermark algorithm can choose an entry above or below the real clock; display FIFO underrun testing is important at high bpp/high clock.

Test signals: use modelist and GTF-derived modes across bpp values, interlaced/doublescan rejection/encoding, polarity combinations, and pixel clocks near watermark table boundaries. Compare programmed register fields against known-good XFree86/i810 values where possible.
