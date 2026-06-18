# Research group subset-b-005554

This grouped report covers the framebuffer driver files requested for `subset-b-005554`. Each source file section is wrapped with reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.c

## Purpose
`atafb.c` is the Atari built-in framebuffer driver. It supports ST/STe, TT, Falcon VIDEL, and external framebuffer adapters through one fbdev front end and a hardware switch table. It translates `fb_var_screeninfo` requests into Atari shifter or VIDEL register programming, allocates or maps video memory, handles palette updates, panning, blanking, and dispatches drawing operations to Atari-specific planar helpers.

## Important APIs, types, and functions
The central private state is `struct atafb_par`, which stores `screen_base`, `yres_virtual`, `next_line`, and a hardware-specific union for TT, ST, and Falcon register state. `struct fb_hwswitch` abstracts hardware operations: `detect`, `encode_fix`, `decode_var`, `encode_var`, `get_par`, `set_par`, `set_screen_base`, `blank`, and `pan_display`.

Backend families are implemented by `tt_*`, `falcon_*`, `stste_*`, and `ext_*` functions. The public fbdev surface is `atafb_ops`, with `fb_check_var`, `fb_set_par`, `fb_blank`, `fb_pan_display`, `fb_fillrect`, `fb_copyarea`, `fb_imageblit`, `fb_ioctl`, default I/O memory read/write, and mmap helpers. `atafb_probe()` selects the backend, allocates or maps framebuffer memory, initializes `fb_info`, chooses a default mode, and registers the framebuffer. `atafb_init()` registers a simple platform device and probes the platform driver on Atari systems.

## Control flow
Boot setup starts with `fb_get_options("atafb", ...)` and `atafb_setup()`, which parses built-in modes, external framebuffer specs, internal overscan geometry, Falcon external clocks, monitor capabilities, `keep`, and user modes. `atafb_probe()` then chooses `ext_switch`, `tt_switch`, `falcon_switch`, or `st_switch` based on explicit external address and `ATARIHW_PRESENT()` probes. It calls the selected `detect()` routine, validates a default mode through `check_default_par()`, allocates ST-RAM or maps external memory, initializes `fb_info.var/fix`, registers the mode list and colormap, then calls `register_framebuffer()`.

Mode validation flows through `atafb_check_var()` to the active backend's `decode_var()`, then back through `encode_var()` so users see rounded and supported geometry. Real mode setting uses `atafb_set_par()`: decode `info->var`, regenerate fixed info under `mm_lock`, and call `ata_set_par()`. Falcon changes are deferred to `falcon_vbl_switcher()` on vertical blank to avoid visible mode-switch glitches.

Drawing clips at the fbdev layer, then dispatches by depth. 1 bpp goes to `atafb_mfb_*`, 2/4/8 bpp interleaved planar modes go to `atafb_iplan2p{2,4,8}_*`, and Falcon 16 bpp truecolor falls back to generic `cfb_*` helpers. Non-1-bit image blits use `c2p_iplan2()`.

## State and persistence behavior
Persistent runtime state is global and driver-lifetime scoped: `fb_info`, `current_par`, `screen_base`, `phys_screen_base`, `screen_len`, monitor flags, setup options, Falcon pending mode state, and external framebuffer configuration. There is no on-disk persistence. Hardware state persists in Atari MMIO/shifter registers until reprogrammed. `current_par_valid` gates whether cached state or hardware state is used. Falcon has asynchronous state transfer through `f_new_mode`, `f_change_mode`, and `f_pan_display` serviced by the VBL IRQ.

## Dependencies and integration points
The driver depends on Atari architecture headers and hardware globals (`asm/atarihw.h`, `asm/atariints.h`, `asm/atari_stram.h`, shifter/VIDEL/MFP/ACIA/YM registers), fbdev core APIs, ST-RAM allocation, interrupt registration, kernel cache mode control, and the local Atari blit helpers declared in `atafb.h`. External framebuffer support uses `ioremap_wt()` and optional VGA DAC I/O mapping. Falcon mode switching integrates with `IRQ_AUTO_4`.

## Risks and edge cases
The driver is hardware-specific and uses global mutable state, raw MMIO/register writes, and panic paths for missing default modes or screen memory. Many mode calculations rely on historic timing constraints and comments call out known limitations for Falcon SM124/TV modes. `atafb_copyarea()` computes clipped widths as unsigned values after destination clipping; bad caller inputs could produce underflow if clipping assumptions are violated. External framebuffer setup trusts boot parameters for physical addresses and lengths. Falcon deferred mode state is shared with an interrupt handler and relies on simple flags. The driver comments note it cannot be unloaded.

## Test signals
Useful validation includes booting on Atari ST/STe, TT, Falcon, and configured external adapter paths; checking `register_framebuffer()` success and reported geometry; running fbdev mode tests for each predefined and user mode; exercising panning and hardware scroll boundaries; palette tests for TT, ST/STE, Falcon, VGA, and MV300 mappings; fbcon text rendering for 1/2/4/8 bpp and Falcon 16 bpp; blank/unblank and kexec shutdown unblank; and stress tests for overlapping copyarea and clipped fill/imageblit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.h

## Purpose
`atafb.h` is the small internal interface between `atafb.c` and the Atari framebuffer drawing helper implementations. It declares depth-specific copy, fill, and 1-bit image linefill routines for monochrome and 2/4/8-plane Atari interleaved planar formats.

## Important APIs, types, and functions
The exported helper families are `atafb_mfb_*`, `atafb_iplan2p2_*`, `atafb_iplan2p4_*`, and `atafb_iplan2p8_*`. Each family exposes `copyarea(struct fb_info *, u_long next_line, ...)`, `fillrect(struct fb_info *, u_long next_line, u32 color, ...)`, and `linefill(struct fb_info *, u_long next_line, ..., const u8 *data, u32 bgcolor, u32 fgcolor)`. The header relies on fbdev types such as `struct fb_info`, `u32`, and `u8` being available from includers.

## Control flow
`atafb.c` includes this header and dispatches generic fbdev drawing requests to one of these prototypes based on `info->var.bits_per_pixel`. The implementation files include the same header to provide definitions matching the front-end calls.

## State and persistence behavior
The header defines no state and no persistence. All state is supplied by the caller through `fb_info`, framebuffer base memory, and the `next_line` stride.

## Dependencies and integration points
This file is tightly coupled to `atafb.c`, `atafb_mfb.c`, `atafb_iplan2p2.c`, `atafb_iplan2p4.c`, and `atafb_iplan2p8.c`. Its signatures encode Atari helper assumptions: byte-addressable framebuffer memory, caller-provided line stride, and fbdev coordinate units.

## Risks and edge cases
Because this is a plain prototype header, the main risks are signature drift between the front end and helper files and missing prerequisite type includes in future users. The helpers assume clipped and mostly byte/word-aligned arguments; the header does not document those preconditions.

## Test signals
Compile coverage is the primary signal. Runtime signals come from `atafb_fillrect`, `atafb_copyarea`, and `atafb_imageblit` successfully resolving to the right helper at 1, 2, 4, and 8 bpp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p2.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p2.c

## Purpose
This file implements low-level fbdev drawing for Atari interleaved bitplanes with 2 planes and 2-byte interleave. It handles 2 bpp copy, rectangle fill, and monochrome glyph/image expansion into planar memory.

## Important APIs, types, and functions
The exported functions are `atafb_iplan2p2_copyarea()`, `atafb_iplan2p2_fillrect()`, and `atafb_iplan2p2_linefill()`. The file sets `BPL` to 2 before including `atafb_utils.h`, which specializes inline helpers such as `expand8_col2mask`, `expand16_col2mask`, `fill8_col`, `fill8_2col`, `fill16_col`, and `memmove32_col` for two planes.

## Control flow
`copyarea()` determines whether the copy is upward/forward or downward/reverse and whether source and destination have compatible 16-pixel alignment. Compatible copies use direct 32-bit moves for full 16-pixel groups and masked column copies for edge halves. Odd/even misaligned copies rebuild shifted plane words with masks and carry values per row. `fillrect()` fills an optional leading 8-pixel half group, a run of 16-pixel groups, and an optional trailing half group. `linefill()` expands 1-bit source data into foreground/background color planes for an optional leading half group, 16-pixel groups, and a trailing half group.

## State and persistence behavior
The functions mutate only the framebuffer memory addressed by `info->screen_base`. No persistent software state is stored. All operation state is stack-local and derived from coordinates, width, height, color, and `next_line`.

## Dependencies and integration points
The file depends on fbdev types, `atafb.h` prototypes, and `atafb_utils.h` specialization through `BPL`. It is called by `atafb.c` when the active mode is 2 bpp and not Falcon 16 bpp.

## Risks and edge cases
The implementation assumes the caller has clipped rectangles and that widths passed to monochrome source expansion are compatible with the font/image data. The copy path contains pointer arithmetic with reverse traversal and masks; off-by-one errors would show as corrupted edge columns or overlap artifacts. Casts between byte pointers and `u32 *` rely on architecture alignment tolerance matching the Atari/m68k target.

## Test signals
Exercise 2 bpp fbcon glyph drawing, rectangle clears, horizontal and vertical overlapping scrolls, unaligned x coordinates, widths crossing 8- and 16-pixel boundaries, and reverse copies where destination is below or to the right of source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p4.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p4.c

## Purpose
This file implements Atari 4 bpp drawing for the 4-plane, 2-byte-interleaved framebuffer layout used by ST low, TT mid, Falcon 16-color-style modes, and related planar configurations.

## Important APIs, types, and functions
It exports `atafb_iplan2p4_copyarea()`, `atafb_iplan2p4_fillrect()`, and `atafb_iplan2p4_linefill()`. It sets `BPL` to 4 and reuses the generic static inline planar helpers from `atafb_utils.h`. With `BPL > 2`, the helper macros expand colors into two `u32` plane words per 16-pixel group.

## Control flow
The structure mirrors the 2-plane helper. `copyarea()` splits same-parity copies from odd/even shifted copies, chooses forward or reverse direction for overlap safety, and copies full groups with direct word moves plus masked column helpers on edges. Misaligned copies carry two plane words (`pval[0]` and `pval[1]`) as they shift data between source and destination positions. `fillrect()` and `linefill()` process a leading half group, full 16-pixel groups, and a trailing half group.

## State and persistence behavior
All state is transient except for writes into framebuffer memory. The functions do not maintain hardware or driver state.

## Dependencies and integration points
The implementation depends on `atafb_utils.h` inline generation with `BPL == 4`, fbdev data structures, and the `atafb.c` dispatcher. It is part of the Atari fbdev software drawing path rather than hardware acceleration.

## Risks and edge cases
The main risk is corruption on boundary conditions: source/destination x alignment differing by 8 pixels, trailing widths not divisible by 16, reverse-overlap copies, and plane-word ordering. Since it writes multiple plane words per logical pixel group, any mismatch with `next_line` or `xres_virtual` produces visually scrambled color planes.

## Test signals
Run 4 bpp fbcon and fbtest patterns, especially scrollback, rectangle clear, stippled glyphs, color palette changes, odd x offsets, and overlapping copies across 8/16-pixel edges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p8.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p8.c

## Purpose
This file implements Atari 8 bpp drawing for the 8-plane, 2-byte-interleaved layout used by 256-color planar modes. It provides copy, solid fill, and 1-bit image expansion for fbdev operations.

## Important APIs, types, and functions
The exported entry points are `atafb_iplan2p8_copyarea()`, `atafb_iplan2p8_fillrect()`, and `atafb_iplan2p8_linefill()`. `BPL` is set to 8 before `atafb_utils.h`, causing color expansion and masked-copy helpers to operate on four `u32` plane words per 16-pixel group.

## Control flow
`copyarea()` handles same-alignment and shifted-alignment cases separately, and chooses forward or reverse traversal for overlap safety. Full aligned groups are copied as repeated `u32` moves. Edge and shifted cases use masks and four carry words so each plane remains in the correct byte lane. `fillrect()` expands an 8-bit color into four plane masks, then fills leading, full, and trailing pixel groups. `linefill()` expands 1-bit source masks into foreground/background plane words.

## State and persistence behavior
No driver state is retained. The only durable effect is modification of framebuffer memory.

## Dependencies and integration points
This is called from `atafb.c` for 8 bpp modes. It depends on fbdev structures, the prototypes in `atafb.h`, and `atafb_utils.h` generated inline helpers.

## Risks and edge cases
The 8-plane variant has the broadest memory write footprint per pixel group, so stride errors and off-by-one calculations can overwrite adjacent lines quickly. Misaligned copies depend on four carry values and two complementary masks; regressions are likely to show as color-plane swapping, vertical streaks, or damaged edge columns.

## Test signals
Use 8 bpp console and graphics tests covering palette entries above 15, solid fills for multiple colors, glyph expansion with distinct foreground/background colors, overlapping scroll in both directions, and x coordinates/widths that begin or end on 8-pixel halves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_iplan2p8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_mfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_mfb.c

## Purpose
`atafb_mfb.c` implements monochrome framebuffer drawing for Atari 1 bpp modes. It provides copy, fill, and 1-bit line blit helpers used by the main Atari fbdev driver.

## Important APIs, types, and functions
The file exports `atafb_mfb_copyarea()`, `atafb_mfb_fillrect()`, and `atafb_mfb_linefill()`. It relies on `fb_memmove`, `fb_memclear`, `fb_memclear_small`, and `fb_memset255` from `atafb_utils.h` for optimized memory movement and clearing.

## Control flow
`copyarea()` has a fast contiguous path when source and destination x are zero and the width equals the line width in pixels. Otherwise it copies row-by-row, forward when the destination is above the source and backward when it is below. `fillrect()` similarly uses a contiguous clear/set path for full-width operations and row-by-row operations otherwise. `linefill()` copies packed source bytes into destination bytes for monochrome font/image rows.

## State and persistence behavior
The helper only changes framebuffer bytes. It does not store software state or touch hardware registers.

## Dependencies and integration points
It is included in the Atari fbdev drawing family through `atafb.h` and called by `atafb.c` for 1 bpp modes. The optimized memory helpers are m68k-oriented and supplied by `atafb_utils.h`.

## Risks and edge cases
The code assumes byte-aligned monochrome widths (`width >> 3`) and x coordinates (`sx >> 3`, `dx >> 3`). Partial-byte edge handling is not implemented here, so correctness relies on the caller/mode constraints providing aligned glyph and rectangle operations. `linefill()` ignores `bgcolor` and `fgcolor` because the source is already monochrome bytes.

## Test signals
Test 1 bpp fbcon text, full-screen clear/set, partial row fills, forward and reverse scroll, and glyph drawing at byte-aligned positions. Visual regressions include dropped edge pixels and wrong scroll direction for overlaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_mfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_utils.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_utils.h

## Purpose
`atafb_utils.h` provides performance-critical memory and planar color helpers for Atari framebuffer drawing. It contains m68k inline assembly replacements for common memory operations and C inline functions specialized by the `BPL` macro for interleaved planar formats.

## Important APIs, types, and functions
General helpers include `fb_memclear_small()`, `fb_memclear()`, `fb_memset255()`, `fb_memmove()`, and `fast_memmove()`. When `BPL` is defined, the header adds color expansion tables (`four2long`, `two2word`) and helpers such as `expand8_col2mask()`, `expand8_2col2mask()`, `fill8_col()`, `fill8_2col()`, `expand16_col2mask()`, `expand16_2col2mask()`, `fill16_col()`, and `memmove32_col()`.

## Control flow
The memory functions choose small unrolled paths or larger aligned block paths and use forward or reverse copying depending on address order. The planar helpers expand a logical color into byte or word masks for the active number of planes, fill packed plane words for 8- or 16-pixel groups, and copy selected columns with masks that preserve untouched planes or half groups.

## State and persistence behavior
The header defines static constant lookup tables and inline functions only. It persists no mutable driver state. Callers persist effects by writing framebuffer memory.

## Dependencies and integration points
This file is included by `atafb_mfb.c` and by the `atafb_iplan2p*.c` files after setting `BPL`. The inline assembly is m68k-specific and assumes the compiler accepts the register constraints and instruction syntax used here.

## Risks and edge cases
The assembly is difficult to audit, architecture-specific, and sensitive to alignment, count underflow, and compiler constraint behavior. `fast_memmove()` assumes a size divisible by 16. The `BPL`-conditional helpers must only be used after defining supported values 2, 4, or 8; otherwise helper expansion would not match the framebuffer layout.

## Test signals
Compile on the target m68k configuration, run framebuffer copy/fill tests for small and large sizes, verify overlapping forward and reverse `fb_memmove()`, and compare planar helper output against known bitplane layouts for 2/4/8 bpp colors and glyph masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atmel_lcdfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/atmel_lcdfb.c

## Purpose
`atmel_lcdfb.c` is an fbdev platform driver for Atmel AT91 LCD controllers. It parses display configuration from device tree, allocates or maps framebuffer memory, programs LCDC DMA and timing registers, supports palettes/pseudo-palettes, backlight/contrast PWM, regulators or GPIO power control, interrupt recovery, and suspend/resume.

## Important APIs, types, and functions
`struct atmel_lcdfb_info` is the primary private state: fb info, MMIO, IRQ, work item, clocks, backlight, pseudo palette, platform data, SoC config, and optional regulator. `struct atmel_lcdfb_config` records SoC feature differences such as alternate pixel clock, HOZVAL support, and old intensity-bit color format.

Key functions include `atmel_lcdfb_check_var()`, `atmel_lcdfb_set_par()`, `atmel_lcdfb_setcolreg()`, `atmel_lcdfb_pan_display()`, `atmel_lcdfb_blank()`, `atmel_lcdfb_interrupt()`, `atmel_lcdfb_task()`, `atmel_lcdfb_of_init()`, `atmel_lcdfb_probe()`, `atmel_lcdfb_remove()`, and PM callbacks. Backlight support is behind `CONFIG_BACKLIGHT_ATMEL_LCDC`.

## Control flow
Probe allocates `fb_info`, parses the `display` phandle for bits per pixel, guard time, `lcdcon2`, `dmacon`, GPIO power controls, wiring mode, backlight flags, and native videomode. It obtains regulator and clocks, enables clocks, validates the selected mode, reserves/maps MMIO, maps a preallocated framebuffer resource or allocates write-combined DMA memory, initializes contrast/backlight, requests IRQ, sets parameters, registers the framebuffer, then powers up the LCD panel.

`check_var()` selects a modelist mode when required, checks pixel clock against `lcdc_clk`, aligns x resolution to four pixels, validates memory size, clamps timing fields to register limits, and configures bitfields for 1/2/4/8/16/24/32 bpp. `set_par()` stops the controller, updates DMA base and frame config, computes and programs the pixel clock divider, writes LCDCON2, timing registers, frame size, FIFO threshold, interrupt masks, waits for DMA idle, and restarts. Underflow IRQ schedules a workqueue reset rather than resetting directly in interrupt context.

## State and persistence behavior
Framebuffer contents persist in mapped preallocated memory or DMA-allocated write-combined memory until freed. Driver state persists in `fb_info->par` for the device lifetime. Hardware state lives in LCDC registers and is rebuilt by `set_par()` or resume. Suspend saves the contrast control register, disables LCD power and clocks, and resume restores clocks, power, contrast, and error interrupts.

## Dependencies and integration points
The driver integrates with the platform bus, Open Firmware display timing APIs, fbdev core, DMA mapping, resource reservation, clk framework, GPIO descriptors, regulator framework, backlight core, workqueues, and Atmel LCDC register definitions in `<video/atmel_lcdc.h>`.

## Risks and edge cases
Probe error unwinding spans many resources and must keep map-vs-DMA framebuffer ownership correct. `atmel_lcdfb_check_var()` is called in probe but its return value is not checked before continuing, so invalid DT modes may fail later or leave adjusted state unexpectedly. Register polling loops wait for busy bits with sleeps and no explicit timeout. Pixel clock divider rounding mutates `info->var.pixclock`; tests need to accept adjusted clocks. Optional GPIO power control skips failed GPIO indexes rather than failing immediately, which may hide incomplete power definitions.

## Test signals
Boot with each compatible string, validate DT parsing failure paths, test 1/2/4/8/16/24/32 bpp mode setup, verify RGB/BGR wiring and old intensity-bit palettes, confirm DMA framebuffer allocation and preallocated-memory mapping paths, induce FIFO underflow and observe workqueue reset, test blank/powerdown, regulator/GPIO power toggles, backlight brightness updates, pan display y-offset updates, and suspend/resume with display restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/atmel_lcdfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/Makefile

## Purpose
This Makefile wires ATI fbdev drivers into the kernel build. It selects object composition for Mach64 `atyfb`, Rage128 `aty128fb`, and Radeon `radeonfb` based on Kconfig symbols.

## Important APIs, types, and functions
The key build variables are `obj-$(CONFIG_FB_ATY)`, `obj-$(CONFIG_FB_ATY128)`, and `obj-$(CONFIG_FB_RADEON)`. Composite object lists are `atyfb-y`, `atyfb-$(CONFIG_FB_ATY_GX)`, `atyfb-$(CONFIG_FB_ATY_CT)`, `atyfb-objs`, `radeonfb-y`, `radeonfb-$(CONFIG_FB_RADEON_I2C)`, `radeonfb-$(CONFIG_FB_RADEON_BACKLIGHT)`, and `radeonfb-objs`.

## Control flow
Kbuild evaluates config symbols and builds `atyfb.o`, `aty128fb.o`, and/or `radeonfb.o`. `atyfb.o` is composed from `atyfb_base.o`, acceleration/cursor objects, and optional Mach64 GX/CT support. `radeonfb.o` is composed from base, power-management, monitor, acceleration, optional I2C, and optional backlight objects. `aty128fb.o` is a single translation unit from `aty128fb.c`.

## State and persistence behavior
The file has no runtime state. Its persistent effect is build graph shape and which objects enter the kernel or module.

## Dependencies and integration points
It integrates with Kbuild and the Kconfig symbols for ATI, Rage128, Radeon, Radeon I2C, and Radeon backlight support. Source file names here must match actual objects in the `aty` directory.

## Risks and edge cases
Incorrect object composition would produce unresolved symbols or omit optional hardware support. Because `atyfb-y` is later assigned to `atyfb-objs`, any future additions must be made before that assignment or use the correct Kbuild pattern.

## Test signals
Build `CONFIG_FB_ATY`, `CONFIG_FB_ATY_GX`, `CONFIG_FB_ATY_CT`, `CONFIG_FB_ATY128`, `CONFIG_FB_RADEON`, `CONFIG_FB_RADEON_I2C`, and `CONFIG_FB_RADEON_BACKLIGHT` combinations as built-in and module where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/ati_ids.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/ati_ids.h

## Purpose
`ati_ids.h` is a local list of ATI PCI chip ID constants, historically kept in sync with XFree86. The comment says this list is currently only used by `radeonfb`.

## Important APIs, types, and functions
The file defines many `PCI_CHIP_*` macros mapping ATI ASIC and board identifiers to 16-bit device IDs. Families include RV/Radeon variants, RS integrated chipsets, R200/R300/R350/R360/R420/R423, Rage128, Mach32, and Mach64 IDs.

## Control flow
There is no executable control flow. Other source files include the header and use the constants in PCI ID tables, chip-family matching, or feature dispatch.

## State and persistence behavior
No runtime state is stored. The constants are compile-time identifiers.

## Dependencies and integration points
The integration point is compile-time use by ATI fbdev drivers, especially Radeon. Values must match PCI device IDs expected by the kernel PCI subsystem and hardware documentation.

## Risks and edge cases
The primary risk is stale or incorrect device ID definitions causing unsupported hardware to be missed or misclassified. Some macro names encode older naming conventions and letter suffixes, so maintainers must avoid duplicate or inconsistent constants when adding IDs.

## Test signals
Build users of the header, inspect generated PCI tables, and test device binding on representative ATI/Radeon/Mach64/Rage128 hardware IDs. Static checks can compare constants against authoritative PCI ID tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/ati_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/aty128fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/aty128fb.c

## Purpose
`aty128fb.c` is the fbdev PCI driver for ATI Rage128 and Rage128 Pro adapters. It maps framebuffer and MMIO BARs, obtains PLL/memory timing information, programs CRTC/PLL/DDA FIFO registers for fbdev modes, supports palette and pseudo-palette updates, optional acceleration engine initialization, M3 LCD/CRT mirroring and backlight, panning, blanking, and PCI power management.

## Important APIs, types, and functions
Important private structures include `struct aty128fb_par`, `struct aty128_crtc`, `struct aty128_pll`, `struct aty128_ddafifo`, `struct aty128_constants`, and `struct aty128_meminfo`. Device matching is in `aty128_pci_tbl`; driver registration is through `aty128fb_driver`.

The fbdev entry points are `aty128fb_check_var()`, `aty128fb_set_par()`, `aty128fb_setcolreg()`, `aty128fb_pan_display()`, `aty128fb_blank()`, `aty128fb_ioctl()`, and `aty128fb_sync()`. Hardware helpers include MMIO/PLL accessors, `register_test()`, FIFO/idle wait functions, `aty128_reset_engine()`, `aty128_init_engine()`, `aty128_map_ROM()`, `aty128_get_pllinfo()`, `aty128_timings()`, `aty128_var_to_crtc()`, `aty128_var_to_pll()`, `aty128_ddafifo()`, and CRTC/PLL/FIFO programming functions.

## Control flow
Module init checks `fb_modesetting_disabled("aty128fb")`, parses boot options when built in, and registers the PCI driver. Probe removes conflicting apertures, enables the PCI device, reserves framebuffer and MMIO BARs, allocates `fb_info`, maps MMIO and VRAM, reads VRAM size, verifies register writes, maps the BIOS or searches legacy x86 ROM space, extracts PLL info when available, fills timing defaults, stores drvdata, and calls `aty128_init()`.

`aty128_init()` identifies the chip, selects a default mode from platform options or mac modes, validates it with `aty128fb_check_var()`, configures DAC and bus-master state, allocates the colormap, initializes the acceleration engine, registers the framebuffer, and optionally registers backlight support. Mode validation decodes `fb_var_screeninfo` into CRTC, PLL, and FIFO register values, checking non-interlaced mode, x alignment, VRAM size, PLL limits, and memory FIFO range. `set_par()` clears interfering blocks, disables video, programs CRTC/PLL/FIFO, applies endian aperture settings, re-enables video, updates `fix`, handles M3 output enables, and initializes acceleration if requested.

## State and persistence behavior
Runtime state persists in `struct aty128fb_par`: register base, VRAM size, chip generation, memory timings, cached CRTC/PLL/FIFO values, palette components, pseudo palette, output routing, suspend flags, FIFO accounting, MTRR/write-combining cookie, and PCI device pointer. Hardware state is stored in Rage128 registers and restored on resume by re-running mode setup, panning, and colormap programming. Framebuffer contents persist in mapped VRAM while the device remains powered.

## Dependencies and integration points
The driver integrates with PCI, aperture conflict removal, fbdev, architecture I/O mapping, optional PowerMac mode/backlight/AGP hooks, optional BootX text update, backlight core, MTRR/write-combining helpers, and Rage128 register definitions from `<video/aty128.h>`.

## Risks and edge cases
The FIFO wait loops reset the engine after long busy polling but have no bounded failure return. BIOS parsing accepts fallback guessed timings when ROM lookup fails. Probe cleanup must balance multiple BAR reservations and mappings. The driver disables bus mastering and I2C paths during mode set, which can affect expectations if future code adds DDC. `aty128fb_setcolreg()` has special 565 handling with cached red/green/blue arrays; palette regressions are easy at 15/16 bpp. M3 LCD/CRT power sequencing and PM paths are platform-specific and guarded by global suspend/blank flags.

## Test signals
Build and bind against Rage128 PCI IDs, verify BAR reservations and register test, boot with and without BIOS PLL data, run fb modes at 8/15/16/24/32 bpp, test panning x alignment and 24 bpp offset handling, verify palette and pseudo-palette colors, exercise blank states and M3 mirror ioctls, test suspend/resume on PowerMac and non-PowerMac PCI paths, validate backlight registration on supported M3 systems, and run fb_sync after accelerated text operations if acceleration is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/aty128fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb.h

## Purpose
`atyfb.h` provides shared core definitions for the ATI Mach64 fbdev driver family. It defines mode, PLL, DAC, acceleration, interrupt, and device-private data structures plus inline MMIO accessors used by Mach64 implementation files.

## Important APIs, types, and functions
Major types are `struct crtc`, `struct aty_interrupt`, `struct pll_info`, `PLL_BLOCK_MACH64`, `struct pll_514`, `struct pll_18818`, `struct pll_ct`, `union aty_pll`, and `struct atyfb_par`. Feature flags are exposed as `M64F_*` bits with `M64_HAS(feature)`. Register accessors are `aty_ld_le32()`, `aty_st_le32()`, `aty_st_le16()`, `aty_ld_8()`, and `aty_st_8()`. Operation tables are `struct aty_dac_ops` and `struct aty_pll_ops`. Acceleration helpers include inline `wait_for_fifo()` and `wait_for_idle()` plus external `aty_reset_engine()`, `aty_init_engine()`, `atyfb_copyarea()`, `atyfb_fillrect()`, and `atyfb_imageblit()`.

## Control flow
This header has no top-level execution. Included implementation files populate `struct atyfb_par`, call DAC/PLL operation tables to translate and program modes, use accessors for register I/O, and use FIFO/idle wait helpers before accelerated commands.

## State and persistence behavior
The state layout in `struct atyfb_par` persists per framebuffer instance: pseudo palette, hardware palette, selected DAC/PLL ops, MMIO base, CRTC/PLL state, timing limits, feature flags, memory and bus metadata, acceleration flags, sleep/blank flags, resource ranges, PCI device, optional SPARC mapping state, optional LCD BIOS data, IRQ state, write-combining cookie, and saved CRTC/PLL for power management.

## Dependencies and integration points
The header depends on Linux I/O, spinlock, waitqueue, PCI, fbdev types via includers, ATI register definitions, and architecture-specific Atari or generic I/O primitives. It declares external DAC, PLL, LCD, cursor, and acceleration symbols implemented in sibling Mach64 files.

## Risks and edge cases
The inline register accessors apply a register-index adjustment for values above `0x400`, which must match the hardware aperture layout. The `aty_st_le16()` generic path uses `writel()` with a 16-bit value, which is intentional or historical but surprising. FIFO wait loops spin without timeout, so a wedged engine can hang callers. The private state is large and conditionally compiled, so feature additions must preserve layout expectations across configs.

## Test signals
Compile Mach64 variants with Atari, SPARC, generic LCD, cursor, acceleration, and PM options. Runtime signals include successful register I/O, mode programming through DAC/PLL ops, accelerated fill/copy/image operations, interrupt-driven vblank state, suspend/resume restoring saved CRTC/PLL, and no hangs in FIFO/idle waits under acceleration stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb.h -->
