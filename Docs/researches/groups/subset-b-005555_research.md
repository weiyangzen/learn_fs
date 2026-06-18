# subset-b-005555 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb_base.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb_base.c

## Purpose

`atyfb_base.c` is the core Linux fbdev driver for ATI Mach64 adapters. It owns the `atyfb` PCI/Atari lifecycle, framebuffer registration, fbdev operations, chip identification, mode validation, CRTC programming, PLL/DAC dispatch, palette programming, panning, vblank waits, suspend/resume, optional LCD/backlight handling, and cleanup. The file is the integration point for the Mach64-specific helper files: acceleration is provided by `mach64_accel.c`, CT-family PLL support by `mach64_ct.c`, GX-family DAC/clock support by `mach64_gx.c`, and hardware cursor support by `mach64_cursor.c`.

## Important APIs, Types, and Functions

The exported fbdev surface is `atyfb_ops`: `atyfb_open()`, `atyfb_release()`, `atyfb_check_var()`, `atyfb_set_par()`, `atyfb_setcolreg()`, `atyfb_pan_display()`, `atyfb_blank()`, `atyfb_ioctl()`, accelerated drawing callbacks, mmap, and sync. `struct atyfb_par` from `atyfb.h` is the central per-device state, holding MMIO bases, selected DAC/PLL ops, CRTC/PLL snapshots, chip features, memory clock limits, acceleration flags, vblank state, IRQ state, PCI resources, saved mode, and optional LCD fields.

Important internal functions include `correct_chipset()` for PCI id and revision matching, `aty_get_crtc()` and `aty_set_crtc()` for hardware register snapshots/programming, `aty_var_to_crtc()` and `aty_crtc_to_var()` for fbdev timing conversion, `atyfb_get_pixclock()` for LCD-aware pixel-clock selection, `aty_init()` for full device initialization, `atyfb_setup_generic()` and `atyfb_setup_sparc()` for PCI resource mapping, `atyfb_pci_probe()` and `atyfb_pci_remove()` for PCI driver binding, `atyfb_blank()` for display power state, and `atyfb_reboot_notify()` for DMI-specific hardware restore on reboot.

## Control Flow

Probe removes conflicting apertures, enables the PCI device, reserves the framebuffer BAR, allocates `fb_info`, maps MMIO and framebuffer apertures, verifies the chipset, optionally reads BIOS/LCD timing data, then calls `aty_init()`. Initialization selects GX or CT DAC/PLL operations, derives clock limits and memory type, saves the incoming CRTC/PLL state, determines real VRAM size, configures MMIO aperture length and write-combining, chooses an initial mode from platform defaults, module parameters, BIOS LCD timings, or `default_var`, validates it through `atyfb_check_var()`, optionally initializes the hardware cursor, allocates the colormap, registers the framebuffer, and registers a backlight device for supported mobile chips.

Mode changes flow through `atyfb_check_var()` and `atyfb_set_par()`. The check path converts fbdev geometry into Mach64 CRTC fields and asks the selected PLL ops to validate the requested pixel clock. The set path repeats the conversion, programs CRTC, DAC, PLL, memory-control bits, DAC mask, line length, visual type, and acceleration engine state. LCD-enabled paths rewrite timing and stretching registers so smaller modes can be scaled or replicated on the panel.

Panning updates `info->var` offsets, recomputes `CRTC_OFF_PITCH`, and either defers the register write to the next vblank interrupt or writes immediately. `FBIO_WAITFORVSYNC` enables vblank IRQs and waits on `par->vblank.wait`. Suspend blanks, resets/parks the engine, optionally powers down PowerMac LCD hardware, marks `par->asleep`, and resumes by restoring memory/PLL state, resetting the mode, and unblanking.

## State and Persistence Behavior

Driver state is volatile and per-device. `par->saved_crtc`, `par->saved_pll`, and `par->mem_cntl` preserve the firmware/boot mode so remove, failed init, reboot notification, and some suspend/resume paths can restore hardware. Module parameters (`noaccel`, `nomtrr`, `vram`, `pll`, `mclk`, `xclk`, `comp_sync`, `mode`, `backlight`, and PowerMac `vmode`/`cmode`) influence initialization but are not persisted by the driver.

Hardware state is persistent only in registers: CRTC timing, PLL programming, memory refresh, DAC palette, LCD power, and acceleration registers. User-visible persistent effects are limited to current framebuffer mode and optional backlight state while the driver is loaded. The driver does not store configuration on disk.

## Dependencies and Integration Points

The file depends on fbdev core, PCI, aperture arbitration, MMIO/ioremap helpers, interrupts/wait queues, console locking, backlight core, DMI reboot notifiers, PowerMac/Atari/Sparc platform hooks, and `<video/mach64.h>` register definitions. It integrates with helper ops through `struct aty_dac_ops`, `struct aty_pll_ops`, and acceleration/cursor functions declared in `atyfb.h`.

## Risks and Edge Cases

The code programs old hardware directly and relies on many chipset-specific magic constants. LCD scaling code is complex and can reject modes larger than the panel unless CRT is enabled. `atyfb_ops` is a static global and `atyfb_set_par()` mutates its `fb_sync` pointer based on one device's acceleration state, which is risky if multiple adapters with different settings are present. Several resource-failure paths rely on staged cleanup and should be fault-injected. Vblank IRQ enable/disable races are controlled with `irq_flags` and `int_lock`, but delayed pan state depends on interrupts being delivered. BIOS parsing uses legacy x86 memory mappings and fixed offsets, so malformed ROM data is a risk.

## Test Signals

Useful coverage includes build tests across PCI, Sparc, PowerMac, Atari, CT, GX, LCD, backlight, and cursor configurations; probe/remove with auxiliary and in-BAR register apertures; mode validation for 8/15/16/24/32 bpp, double-scan/interlace, LCD panel scaling, and VRAM limits; acceleration enabled/disabled transitions; panning with and without `FB_ACTIVATE_VBL`; `FBIO_WAITFORVSYNC` timeout and IRQ delivery; suspend/resume and reboot notifier restore; palette programming in pseudocolor and directcolor modes; and fault injection for ioremap, memory-region, colormap, IRQ, and framebuffer registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_accel.c

## Purpose

`mach64_accel.c` implements Mach64 2D acceleration for the `atyfb` framebuffer driver. It resets and initializes the GUI engine, sets the standard drawing context, and provides accelerated fbdev `copyarea`, `fillrect`, and `imageblit` callbacks with software fallbacks when acceleration is unavailable or inappropriate.

## Important APIs, Types, and Functions

The externally used functions are `aty_reset_engine()`, `aty_init_engine()`, `atyfb_copyarea()`, `atyfb_fillrect()`, and `atyfb_imageblit()`. `rotation24bpp()` computes Mach64's 24-bpp byte-rotation control for left-to-right or right-to-left operations because the engine operates in 8-bpp units for 24-bpp modes. `reset_GTC_3D_engine()` resets the RagePro/GTC 3D block for chips carrying `M64F_RESET_3D`. `draw_rect()` writes `DST_Y_X` and `DST_HEIGHT_WIDTH` and marks `par->blitter_may_be_busy`.

The file depends on FIFO/idle helpers from `atyfb.h`, register names and bit definitions from `<video/mach64.h>`, and fbdev software helpers `cfb_copyarea()`, `cfb_fillrect()`, and `cfb_imageblit()`.

## Control Flow

`aty_init_engine()` derives pitch and virtual width from `fb_info`; in 24-bpp it multiplies horizontal quantities by three. It optionally resets the 3D engine, resets the GUI engine, initializes VGA page pointers, then writes a standard context: destination/source pitch, source/destination defaults, host and pattern state, scissor bounds, foreground/background colors, write mask, mix mode, source selection, color compare, pixel width, chain mask, and miscellaneous 3D/interrupt/trajectory controls. It finishes with `wait_for_idle()`.

`atyfb_copyarea()` rejects sleeping devices and empty rectangles, falls back if `par->accel_flags` is zero, adjusts 24-bpp coordinates, chooses copy direction for overlap safety, computes 24-bpp rotation when needed, writes source/destination state, and starts the rectangle blit. `atyfb_fillrect()` resolves the fill color through `pseudo_palette` for true/direct color visuals, adjusts 24-bpp width and rotation, writes foreground and source/mix controls, then starts a rectangle fill. `atyfb_imageblit()` accelerates 1-bpp monochrome and same-depth image uploads, configures host pixel width and colors, starts the destination rectangle, and streams image data through `HOST_DATA0`; unsupported depth combinations fall back to `cfb_imageblit()`.

## State and Persistence Behavior

The persistent runtime state is in hardware registers plus `par->fifo_space` and `par->blitter_may_be_busy`. Engine reset clears cached FIFO accounting. Drawing operations set `blitter_may_be_busy` so `atyfb_sync()` or later mode-setting can wait for idle before touching state that must not race with the blitter. No file-backed state is maintained.

## Dependencies and Integration Points

This file is called from `atyfb_base.c` through `atyfb_ops` and from mode setup via `aty_init_engine()`. Correctness depends on `par->crtc.dp_pix_width`, `par->crtc.dp_chain_mask`, `info->fix.line_length`, `info->var.bits_per_pixel`, and `par->accel_flags` being prepared by `atyfb_set_par()`. The code also relies on endian-safe image reads via `get_unaligned_le32()` and writes through the driver's MMIO accessors.

## Risks and Edge Cases

24-bpp support is the most fragile path: coordinates are tripled, rotations depend on direction, and monochrome image expansion either uses `DP_HOST_TRIPLE_EN` only for aligned widths or manually triples bits. The manual expansion loop is easy to regress around non-byte-aligned widths. None of the accelerated paths clip rectangles locally; fbdev core is expected to provide valid regions, unlike the Radeon helpers that clamp. If acceleration is invoked while asleep, operations are silently ignored. FIFO waits must match the number of following register writes.

## Test Signals

Test mode switches into 8, 15, 16, 24, and 32 bpp with acceleration on and off; overlapping copy left/right and up/down; zero-size operations; truecolor and pseudocolor fills; monochrome imageblits with widths not divisible by 8; same-depth image uploads; 24-bpp glyph rendering with and without hardware triple support; sync after operations; and suspend paths that call drawing functions while `par->asleep` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_ct.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_ct.c

## Purpose

`mach64_ct.c` supplies PLL, clock, and DSP FIFO programming for integrated Mach64 CT/VT/GT/LT-family chips. It implements the `aty_pll_ops` and `aty_dac_ops` entries used by `atyfb_base.c` when `M64F_INTEGRATED` devices are detected.

## Important APIs, Types, and Functions

The external register helpers are `aty_ld_pll_ct()` and the internal `aty_st_pll_ct()`. The main PLL callbacks are `aty_var_to_pll_ct()`, `aty_pll_to_var_ct()`, `aty_set_pll_ct()`, `aty_get_pll_ct()`, `aty_init_pll_ct()`, and `aty_resume_pll_ct()`, collected in `aty_pll_ct`. `aty_dac_ct` is a dummy DAC op because integrated CT-family output setup is mostly handled elsewhere. `aty_dsp_gt()` calculates `DSP_CONFIG` and `DSP_ON_OFF` for GTB-DSP chips, while `aty_valid_pll_ct()` validates and derives VCLK feedback/post-dividers. `aty_postdividers[]` maps encoded post-divider values to real divisors.

## Control Flow

Mode validation calls `aty_var_to_pll_ct()`, which derives a VCLK divider set from the requested pixel-clock period and, for GTB-DSP chips, computes FIFO thresholds using memory clock, pixel clock, bpp, RAM type, FIFO size, and optional LCD scaling state. `aty_pll_to_var_ct()` converts the chosen PLL fields back into a fbdev pixel-clock period.

`aty_set_pll_ct()` temporarily disables LCD output when required, strobes the selected clock, enables accelerator display if needed, resets VCLK, writes post-divider, extended divider, feedback divider, PLL general control, and VCLK control registers, waits for lock, restores display mode, then programs DLL and DSP registers for GTB-DSP chips. `aty_get_pll_ct()` snapshots current PLL registers for restore. `aty_init_pll_ct()` derives base memory-clock and FIFO timing state from current PLL and `MEM_CNTL`, applies RAM-type latency rules, honors BIOS DSP loop latency when present, and either leaves existing memory clocks alone or computes new MCLK/XCLK/SCLK values from driver limits. `aty_resume_pll_ct()` restores reference, general, memory, extended, and optional SCLK state in the required order.

## State and Persistence Behavior

All durable driver state is stored in `par->pll.ct` and `par->pll_limits`. `aty_init_pll_ct()` populates fields such as `pll_ref_div`, `mclk_fb_div`, post-dividers, FIFO size, loop latency, XCLK delays, and feature flags. `aty_set_pll_ct()` persists mode state in hardware PLL/DSP registers until the next mode set, suspend/resume, or driver removal. There is no disk persistence, but bad PLL programming can leave display hardware unusable until reset or restore.

## Dependencies and Integration Points

The file depends on `atyfb_base.c` for chip feature flags, memory type, LCD dimensions, and clock limits. It writes Mach64 PLL registers through indexed `CLOCK_CNTL_ADDR/DATA` and normal MMIO for DSP registers. LCD support uses `aty_ld_lcd()` and `aty_st_lcd()` from the base file. PowerMac-specific clock handling checks `machine_is(powermac)`.

## Risks and Edge Cases

Clock arithmetic uses integer periods and dividers with tight range checks. Out-of-range pixel, memory, or chip clocks return `-EINVAL`, which rejects mode setting. FIFO/DSP calculations are sensitive to RAM type, FIFO size, LCD scaling, and bpp; mistakes can produce underflow or display corruption. The code carries comments about SCLK ordering because disabling SCLK before it is used can crash systems. The `pll->ct.xres` LCD scaling adjustment must be reset by the caller's pixel-clock path. Some paths preserve existing memory clocks when `par->mclk_per == 0`, making behavior depend on firmware initialization.

## Test Signals

Coverage should include CT, VT, GT, LT, XL, and Mobility variants; GTB-DSP and non-DSP chips; DRAM, EDO, SDRAM, SGRAM, WRAM, and SDRAM32 memory types; default and user-overridden `pll`, `mclk`, and `xclk`; 14.31818 MHz and 29.498928 MHz reference clocks; LCD scaling mode changes; suspend/resume restore; and invalid pixel-clock requests. Hardware validation should watch for FIFO underruns, PLL lock delays, and display corruption during rapid mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_cursor.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_cursor.c

## Purpose

`mach64_cursor.c` implements hardware cursor support for Mach64 CT/VT/GT/LT devices. It reserves one page at the end of framebuffer memory for a 64x64 two-bit cursor image, translates fbdev cursor requests into Mach64 cursor registers and image memory, and installs the cursor callback into `atyfb_ops`.

## Important APIs, Types, and Functions

The public entry point is `aty_init_cursor()`, which reduces `info->fix.smem_len`, maps or selects the cursor sprite memory, initializes `info->sprite`, and assigns `atyfb_cursor()` to `fb_ops->fb_cursor`. `atyfb_cursor()` handles enable/disable, position, color map, shape, and image updates. `cursor_bits_lookup[]` converts four 1-bpp source bits into packed two-bit hardware cursor pixels, and `comp()` applies masks for partial final bytes.

## Control Flow

Initialization subtracts `PAGE_SIZE` from usable framebuffer memory, places the cursor storage at the new end of VRAM, and handles platform differences: Sparc uses a special offset, big-endian systems ioremap a hardware address, and little-endian systems use `screen_base + smem_len`. The sprite is declared as IO pixmap memory with 16-byte scan and buffer alignment.

`atyfb_cursor()` first rejects Sparc mmap ownership conflicts and sleeping devices. It toggles `HWCURSOR_ENABLE` in `GEN_TEST_CNTL`. For position updates it subtracts the hotspot and current framebuffer pan offsets, converts negative positions into horizontal/vertical cursor offsets, doubles vertical coordinates in double-scan mode, then writes `CUR_OFFSET`, `CUR_HORZ_VERT_OFF`, and `CUR_HORZ_VERT_POSN`. For color updates it derives foreground/background colors from the fbdev colormap and writes `CUR_CLR0`/`CUR_CLR1`. For shape or image updates it clears the 1024-byte cursor bitmap to the transparent pattern `0xaa`, then walks source and mask bytes and emits packed two-bit cursor pixels for `ROP_XOR` or `ROP_COPY`, padding partial trailing pixels as transparent.

## State and Persistence Behavior

The cursor image persists in a reserved VRAM page for the life of the mode/device, and cursor enable, position, colors, and offsets persist in Mach64 cursor registers. The driver reduces available framebuffer memory so normal fbdev drawing does not overwrite the cursor image. There is no saved software copy of the cursor image in this file beyond fbdev-provided structures during update calls.

## Dependencies and Integration Points

This file depends on fbdev cursor structures, `info->sprite`, the base driver's CRTC state for double-scan detection, `info->var` offsets for panning compensation, and Mach64 cursor register definitions. It is only initialized by `aty_init()` for integrated CT-family devices when acceleration is not globally disabled.

## Risks and Edge Cases

The cursor storage reservation changes `smem_len`, so ordering with VRAM sizing and mode validation matters. Negative positions are handled through offsets, but very large cursors or hotspots outside expected fbdev bounds could stress the arithmetic. Only `ROP_XOR` and `ROP_COPY` are explicitly handled. The code clears a fixed 1024-byte cursor area and assumes 64x64 hardware format; larger fbdev cursor images would not fit correctly. On big-endian systems the ioremap must be released by the base cleanup path. Sparc mmap users block hardware cursor updates to avoid conflicting direct hardware access.

## Test Signals

Test cursor enable/disable, movement with panned displays, negative x/y positions, nonzero hotspots, double-scan modes, colormap changes, XOR and COPY cursors, widths not divisible by eight, repeated shape updates, and teardown on big-endian mappings. Also test with acceleration disabled to confirm cursor initialization is skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_cursor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_gx.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_gx.c

## Purpose

`mach64_gx.c` implements DAC and external clock-chip support for older Mach64 GX/CX adapters. It provides `aty_dac_ops` and `aty_pll_ops` instances for IBM RGB514, ATI 68860-B, AT&T 21C498, ATI 18818/ICS2595, STG1703, Chrontel 8398, AT&T 20C408, and fallback unsupported devices.

## Important APIs, Types, and Functions

Important helper routines are `aty_dac_waste4()` for DAC counter synchronization, `aty_StrobeClock()` for clock-control strobing, `aty_st_514()` for indexed IBM RGB514 writes, and `aty_ICS2595_put1bit()` for serial clock programming. DAC callbacks include `aty_set_dac_514()`, `aty_set_dac_ATI68860_B()`, `aty_set_dac_ATT21C498()`, and `aty_set_dac_unsupported()`. PLL callbacks include `aty_var_to_pll_514()`, `aty_set_pll_514()`, `aty_var_to_pll_18818()`, `aty_set_pll18818()`, `aty_var_to_pll_1703()`, `aty_set_pll_1703()`, `aty_var_to_pll_8398()`, `aty_set_pll_8398()`, `aty_var_to_pll_408()`, and `aty_set_pll_408()`.

## Control Flow

The base driver selects one of these ops during GX initialization based on detected DAC and clock subtype. Mode validation calls the selected `var_to_pll` function, which converts a fbdev pixel-clock period into the target chip's encoded divider/programming word. For IBM RGB514 the code uses a fixed table of known modes. For ICS2595, STG1703, Chrontel 8398, and AT&T 20C408 it computes divider fields within chip-specific min/max frequency constraints. Mode setting then calls the DAC setter to configure pixel format and memory/DAC control bits, followed by the PLL setter to write the encoded clock word through DAC-indexed or serial control sequences.

Each DAC setter chooses register values based on bpp and sometimes acceleration mode or dot clock. The 68860 and unsupported paths write Mach64 `BUS_CNTL` and `DAC_CNTL` defaults. Clock setters temporarily force extended display enable where needed, program the external clock chip, clear DAC counters, and restore CRTC/display control state.

## State and Persistence Behavior

The file stores no long-lived software state beyond constants and callback tables. PLL choices are stored in `union aty_pll`, mainly `pll_514` or `pll_18818` fields, and then persisted in external DAC/clock hardware registers. `period_in_ps` is retained for many `pll_to_var` callbacks instead of recomputing from programmed bits, so reporting reflects requested timing rather than a full hardware readback.

## Dependencies and Integration Points

This file integrates with `atyfb_base.c` through `struct aty_dac_ops` and `struct aty_pll_ops`. It uses `struct atyfb_par` for MMIO bases, `clk_wr_offset`, reference clock period, VRAM size, and accessors. It depends heavily on `<video/mach64.h>` register and bit definitions and on delay helpers for hardware settle times.

## Risks and Edge Cases

Older DAC/clock programming is based on tables, approximations, and legacy magic values. Some callbacks clamp frequencies instead of failing, while others return `-EINVAL`; mode behavior differs by chip. Several `pll_to_var` callbacks simply return the requested period, not a calculated effective clock. Unsupported DAC/PLL ops are dummy or generic register writes, so display may be unreliable on unimplemented hardware. The serial ICS2595 programming sequence and DAC counter synchronization are timing-sensitive. Bpp handling varies by DAC, and 24/32-bpp modes share settings on some chips.

## Test Signals

Test with real or emulated GX/CX adapters using each supported DAC/clock combination where possible. Validate 8, 15, 16, 24, and 32 bpp mode set, accelerated versus unaccelerated DAC setup, pixel-clock boundary values, invalid high/low clocks, restoration of CRTC extended display state, and repeated mode switches. Static review should focus on integer divider search bounds and cases where frequency clamping may hide invalid modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_gx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_accel.c

## Purpose

`radeon_accel.c` implements Radeon fbdev 2D acceleration setup and drawing primitives for `radeonfb`, separate from the Mach64 driver but located in the same `aty` fbdev directory. It initializes and resets the Radeon 2D engine, provides accelerated fill and copy operations, synchronizes with the engine, and falls back to software image blitting.

## Important APIs, Types, and Functions

Public functions are `radeonfb_fillrect()`, `radeonfb_copyarea()`, `radeonfb_imageblit()`, `radeonfb_sync()`, `radeonfb_engine_reset()`, and `radeonfb_engine_init()`. Internal helpers are `radeon_fixup_offset()`, `radeonfb_prim_fillrect()`, and `radeonfb_prim_copyarea()`. The code uses Radeon register macros such as `INREG`, `OUTREG`, `OUTREGP`, `INPLL`, `OUTPLL`, `radeon_fifo_wait()`, `radeon_engine_idle()`, `radeon_engine_flush()`, and `radeon_get_dstbpp()`.

## Control Flow

Every accelerated fill/copy first checks `info->state` and falls back if `FBINFO_HWACCEL_DISABLED` is set. `radeon_fixup_offset()` rereads `MC_FB_LOCATION` and updates default, destination, and source pitch/offset registers if firmware or X changed the card's framebuffer base behind the driver's cached state. Fill validates and clips the rectangle to virtual resolution, writes `DP_GUI_MASTER_CNTL`, brush color, write mask, direction, flush/idleness controls, and destination rectangle registers. Copy similarly validates and clips source and destination bounds, adjusts starting coordinates and direction for overlaps, configures source-memory blit state, flushes, and writes source/destination/size registers.

`radeonfb_imageblit()` waits for engine idle and delegates to `cfb_imageblit()` rather than accelerating image upload. `radeonfb_sync()` idles the engine. `radeonfb_engine_reset()` flushes the engine, forces memory clocks on, applies RBBM soft resets with R300-specific differences, resets host data path, restores clock/reset registers, and handles cache mode quirks. `radeonfb_engine_init()` disables 3D, resets the engine, configures destination cache mode, rereads framebuffer location, writes pitch/offsets, sets endian mode, default scissor, GUI master control, line/brush/source/write-mask defaults, and idles the engine.

## State and Persistence Behavior

Long-lived state is in `struct radeonfb_info`: `fb_local_base`, `pitch`, `depth`, `dp_gui_master_cntl`, `pseudo_palette`, family flags, and MMIO/PLL access context. Hardware register programming persists until the next engine reset, mode set, X handoff, suspend/resume, or driver unload. There is no disk-backed state.

## Dependencies and Integration Points

The file integrates with `radeonfb` via `radeonfb.h` and the fbdev operation table defined elsewhere. It depends on Radeon register definitions from `<video/radeon.h>`, fbdev software helpers, and chip-family helpers `IS_R300_VARIANT()`. It is designed to tolerate firmware/X server changes by checking framebuffer base before each accelerated operation.

## Risks and Edge Cases

The offset fixup is a workaround for potentially dangerous stale engine offsets; if it fails or is skipped, acceleration can write to the wrong memory. Fill and copy clip to virtual resolution, but arithmetic should still be checked for overflow on unusual modes. Image blit is software-only after idling, so glyph performance is lower but safer. Reset paths differ for R300 variants and older chips; wrong family detection can leave blocks reset or cache behavior wrong. The code relies on busy-wait FIFO/idle macros and direct MMIO ordering.

## Test Signals

Test accelerated fill/copy on 8/16/24/32-bpp modes, clipping at each edge, overlapping copies in all directions, disabled acceleration fallback, `FBINFO_STATE_RUNNING` gating, software image blit after accelerated operations, engine sync, engine init after mode set, and simulated `MC_FB_LOCATION` changes before fill/copy. Hardware tests should cover R300 and non-R300 families and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_backlight.c

## Purpose

`radeon_backlight.c` connects Radeon laptop LVDS backlight control to the Linux backlight subsystem. It registers a raw backlight device for LCD panels, maps fbdev brightness curves to Radeon LVDS modulation levels, powers the panel/backlight on and off through LVDS registers, and unregisters the device on teardown.

## Important APIs, Types, and Functions

The public functions are `radeonfb_bl_init()` and `radeonfb_bl_exit()`. `struct radeon_bl_privdata` stores the owning `struct radeonfb_info` and whether brightness polarity is inverted. `radeon_bl_get_level_brightness()` maps a fbdev backlight level through `info->bl_curve` into the hardware range `0x00..0xff`, with optional inversion. `radeon_bl_update_status()` is the backlight core callback and is installed through `radeon_bl_data`.

## Control Flow

Initialization exits unless the primary monitor is LCD. On PowerMac builds it also checks for compatible ATI/MNCA backlight types. It allocates private data, registers a `BACKLIGHT_RAW` device named `radeonblN`, chooses negative brightness polarity based on chip family and selected PowerBook models, stores the device in `rinfo->info->bl_dev`, initializes the default brightness curve, sets brightness to max and power on, and calls `backlight_update_status()`.

`radeon_bl_update_status()` ignores non-LCD outputs. For positive brightness it deletes any pending LVDS timer, idles the engine, clears display-disable, ensures digital/LVDS/backlight enable bits are set in the correct sequence, programs `LVDS_BL_MOD_LEVEL`, optionally delays final `LVDS_ON` state through `rinfo->lvds_timer`, and mirrors state bits into `rinfo->init_state.lvds_gen_cntl`. For zero brightness it clears LVDS always-on pixel clock on mobility/IGP chips, disables modulation/backlight/display, clears LVDS enable and digital-on in stages with required delays, schedules delayed panel power state, then restores pixel-clock control.

Teardown unregisters the backlight device, frees private data, clears `bl_dev`, and logs unload.

## State and Persistence Behavior

Persistent runtime state lives in the backlight device properties, `rinfo->info->bl_curve`, `struct radeon_bl_privdata`, `rinfo->pending_lvds_gen_cntl`, and `rinfo->init_state.lvds_gen_cntl`. Hardware LVDS state persists in `LVDS_GEN_CNTL` and `PIXCLKS_CNTL`. The code intentionally updates `init_state.lvds_gen_cntl` so later mode/power restore logic tracks the latest panel state rather than stale boot values.

## Dependencies and Integration Points

The file depends on the Linux backlight core, `radeonfb.h`, Radeon MMIO/PLL macros, the Radeon LVDS timer managed elsewhere in the driver, fbdev backlight curve helpers, and optional PowerMac backlight/platform checks. It assumes `rinfo->panel_info.pwr_delay`, `rinfo->lvds_timer`, monitor type, family, mobility/IGP flags, and initial LVDS state are initialized by the main Radeon driver.

## Risks and Edge Cases

Panel power sequencing is timing-sensitive; wrong ordering can blank, flicker, or fail to wake a panel. Brightness polarity is determined by family/model heuristics and may be wrong for unknown panels. `timer_delete_sync()` and later `mod_timer()` must coordinate with the LVDS timer callback elsewhere. The update path idles the graphics engine and touches PLL bits, so it should not race with suspend/resume or mode-setting. Allocation failure after private data creation is handled by a shared error path that frees `pdata`.

## Test Signals

Test registration only on LCD outputs, PowerMac gating, brightness min/max/mid values, inverted and non-inverted polarity families, zero-brightness powerdown, nonzero powerup from off, repeated rapid brightness changes, suspend/resume interaction, LVDS timer behavior with `panel_info.pwr_delay`, mobility/IGP pixel-clock workaround, and clean unregister with no stale `bl_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_backlight.c -->
