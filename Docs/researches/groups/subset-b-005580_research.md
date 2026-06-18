# subset-b-005580 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/skeletonfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/skeletonfb.c

## Purpose
`skeletonfb.c` is not a production framebuffer driver. It is an in-tree fbdev template explaining how a driver should structure `struct fb_info`, private `par` state, `fb_ops`, mode validation, color handling, acceleration hooks, probe/remove, PM, and boot-option setup. The comments document fbdev API expectations and common mistakes, while the code intentionally contains placeholders such as `struct xxx_par`, `framebuffer_virtual_memory`, `write_{red|green|blue|transp}_to_clut()`, `pdev`, and `xxxfb_*` callbacks that a real driver must replace.

## Important APIs, types, and functions
- Static examples: `mode_option`, `xxxfb_fix`, the sample global `fb_info info`, and `current_par`.
- fbdev operation examples: `xxxfb_open()`, `xxxfb_release()`, `xxxfb_check_var()`, `xxxfb_set_par()`, `xxxfb_setcolreg()`, `xxxfb_pan_display()`, `xxxfb_blank()`, `xxxfb_fillrect()`, `xxxfb_copyarea()`, `xxxfb_imageblit()`, `xxxfb_cursor()`, and `xxxfb_sync()`.
- Registration examples: `xxxfb_probe()`, `xxxfb_remove()`, `xxxfb_init()`, `xxxfb_exit()`, PCI `xxxfb_driver`, platform `xxxfb_driver`, and optional suspend/resume variants.
- Kernel APIs demonstrated include `framebuffer_alloc()`, `framebuffer_release()`, `fb_find_mode()`, `fb_alloc_cmap()`, `register_framebuffer()`, `unregister_framebuffer()`, `fb_get_options()`, `fb_modesetting_disabled()`, `aperture_remove_conflicting_pci_devices()`, `pci_register_driver()`, and platform-device registration.

## Control flow
The template shows the normal fbdev path: parse module/boot options, allocate `fb_info` plus private state, remove conflicting firmware apertures, map framebuffer memory, attach `fb_ops`, select a mode through modedb or a fixed `var`, allocate a colormap, optionally initialize hardware, then register the framebuffer. Runtime calls enter through `fb_ops`: `check_var` validates and adjusts a proposed mode without touching `info->var`, `set_par` programs hardware from the accepted `info->var`, `setcolreg` programs CLUT or pseudo-palette entries, panning and blanking update display state, and drawing/cursor/sync callbacks either use hardware acceleration or generic helpers. Remove unregisters the framebuffer, frees the colormap, tears down device resources, and releases `fb_info`.

## State and persistence behavior
The file distinguishes durable device state from fbdev state. `struct xxx_par` is the intended hardware-state container and may be shared by multiple `fb_info` instances on multi-head hardware or held as an array for multi-stage graphics pipelines. `fb_info.fix`, `fb_info.var`, `fb_info.cmap`, `fb_info.pseudo_palette`, and `fb_info.pixmap` hold fbdev-visible state. The comments emphasize that `check_var` may mutate only the proposed `var`, not the registered `info->var`, while `set_par` may update `par` and `fix` but uses the already-accepted `info->var`. Suspend/resume examples show where a real driver would save and restore hardware state.

## Dependencies and integration points
This template depends on fbdev core headers and bus infrastructure (`linux/fb.h`, PCI, platform devices, aperture handling, module init/exit, memory allocation, I/O mapping). It integrates conceptually with fbcon through `fb_ops`, pseudo-palette conventions, acceleration flags, and pixmap alignment fields. It also documents the relationship between driver mode handling and `modedb.c`/`fb_find_mode()`.

## Risks
Because this is example code, it should not be built or treated as a working driver. Several identifiers are undefined, some declarations are inconsistent (`pdev` in the PCI probe example, platform type typos), and the pseudocode omits resource cleanup details. The technical risk for consumers is copying the skeleton too literally instead of adapting the documented contracts: mutating `info->var` outside `check_var`, implementing dummy pan/blank callbacks when hardware cannot support them, confusing `bits_per_pixel` with color depth, or mishandling truecolor/directcolor pseudo-palette rules.

## Test signals
There are no direct runtime tests for `skeletonfb.c`; useful signals are compile-time only after a developer replaces placeholders with real hardware code. Derived drivers should be tested for probe/remove cleanup, mode validation failure paths, fbcon rendering, palette updates across pseudocolor/truecolor/directcolor modes, mmap/read/write behavior, panning and blanking support only when advertised, acceleration sync correctness, boot-option parsing, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/skeletonfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm501fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sm501fb.c

## Purpose
`sm501fb.c` is the framebuffer driver for the Silicon Motion SM501 display controller. It supports two display heads, CRT and panel, sharing one SM501 device state while exposing each enabled head as a separate fbdev framebuffer. The driver maps display-controller registers, 2D engine registers, and framebuffer memory; allocates SM501-local memory for CRT/panel scanout and hardware cursors; programs timings, clocks, palettes, panel power sequencing, CRT routing, and basic 2D acceleration; and handles suspend/resume by saving framebuffer and cursor contents.

## Important APIs, types, and functions
- State types: `enum sm501_controller`, `struct sm501_mem`, shared `struct sm501fb_info`, and per-framebuffer `struct sm501fb_par`.
- Mode and memory helpers: `sm501_alloc_mem()`, `sm501fb_ps_to_hz()`, `sm501fb_setup_gamma()`, `sm501fb_check_var()`, `sm501fb_set_par_common()`, and `sm501fb_set_par_geometry()`.
- Per-head callbacks: `sm501fb_check_var_crt()`, `sm501fb_check_var_pnl()`, `sm501fb_set_par_crt()`, `sm501fb_set_par_pnl()`, `sm501fb_pan_crt()`, `sm501fb_pan_pnl()`, `sm501fb_blank_crt()`, and `sm501fb_blank_pnl()`.
- Color/cursor/acceleration: `sm501fb_setcolreg()`, `sm501fb_cursor()`, `sm501fb_sync()`, `sm501fb_copyarea()`, and `sm501fb_fillrect()`.
- Sysfs/debug: `crt_src`, `fbregs_crt`, `fbregs_pnl`, and `ATTRIBUTE_GROUPS(sm501fb)`.
- Lifecycle and PM: `sm501fb_probe()`, `sm501fb_probe_one()`, `sm501fb_start()`, `sm501fb_init_fb()`, `sm501fb_start_one()`, `sm501fb_remove()`, `sm501fb_suspend_fb()`, `sm501fb_resume_fb()`, `sm501fb_suspend()`, and `sm501fb_resume()`.

## Control flow
Probe allocates `sm501fb_info`, obtains platform data or default/of-derived data, creates `fb_info` instances for the configured CRT and panel heads, maps register/2D/framebuffer resources in `sm501fb_start()`, powers the display and 2D units, initializes cursor memory for each head, initializes each framebuffer, and registers it. `sm501fb_init_fb()` selects head-specific ops, applies platform flags such as hardware cursor enablement, constructs a modelist from EDID when present, chooses a default or supplied mode, allocates the colormap, and validates the mode. Runtime `set_par` flows through common memory allocation and clock programming, then writes per-head panning, timing, geometry, bpp, gamma, and enable bits. CRT panning writes byte-offset and pixel-offset fields; panel panning writes width/height offset registers. Sysfs `crt_src` switches whether the CRT output uses CRT or panel data.

## State and persistence behavior
Shared state in `sm501fb_info` includes mapped resources, platform data, fbmem length, IRQ number, EDID, and saved CRT control bits for PM. Per-head state in `sm501fb_par` includes the head id, screen allocation, cursor allocation, private copied `fb_ops`, pseudo-palette, cursor register base, and suspend backing stores. SM501 framebuffer memory is carved manually from a single resource: CRT starts low, panel is placed high with page alignment, cursor blocks are taken from the end, and acceleration space is implicitly the gap. Suspend blanks each active head, marks fbdev suspended under `console_lock()`, `vmalloc()`s copies of scanout and cursor memory, copies from I/O memory, and powers off the display gate. Resume powers the unit, restores saved CRT routing bits, re-runs set_par, copies saved screen/cursor data back to I/O memory, clears suspend, and frees the temporary buffers.

## Dependencies and integration points
The driver is a platform driver named `sm501-fb` and depends on the SM501 MFD/core APIs and register definitions in `linux/sm501.h` and `linux/sm501-regs.h`. It uses fbdev core, modedb/EDID helpers, generic cfb imageblit, I/O memory accessors, platform resources, optional device tree properties for endian/EDID/mode, sysfs device attributes, and SM501 clock/power helpers (`sm501_set_clock()`, `sm501_unit_power()`, `sm501_misc_control()`, `sm501_modify_reg()`). Module parameters `mode` and `bpp` influence initial mode selection.

## Risks
Memory carving is order-dependent and sensitive to virtual resolution and fbmem size. `sm501_alloc_mem()` updates `fbmem_len` for cursor allocation and computes panel/CRT overlap manually, so unusual head combinations or repeated mode changes can expose allocation bugs. EDID handling frees `info->edid_data` in one framebuffer initialization path, which is shared device state and must not be reused unexpectedly. Acceleration clipping subtracts one when a rectangle reaches the virtual boundary, risking off-by-one underdraw. Hardware cursor color indexing trusts `info->cmap` entries selected by fbcon. Suspend copies can fail independently per head; the top-level suspend ignores return values and still powers down. Remove calls colormap deallocation before unregistering, which may be unusual relative to fbdev lifetime expectations.

## Test signals
Important tests include probing with CRT-only, panel-only, and dual-head platform data; mode selection from platform default, module mode, and EDID; 8/16/32 bpp color layout including `SM501_FBPD_SWAP_FB_ENDIAN`; CRT source switching through sysfs; panel power sequencing and blank/unblank; hardware cursor shape/position/color limits; pan display on both heads; accelerated `copyarea`/`fillrect` including boundary clipping and overlapping copies; suspend/resume with visible framebuffer and cursor restoration; and remove/failure-path cleanup of mapped resources and framebuffer registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm501fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712.h

## Purpose
`sm712.h` is the private header for the Silicon Motion SM7xx framebuffer driver. It defines default panel dimensions, register access macros, VGA register block sizes, the `struct modeinit` table layout used by `sm712fb.c`, and endian-specific pixel/address helpers. The header centralizes low-level VGA-style indexed register writes for sequencer, graphics, attribute, and CRTC programming.

## Important APIs, types, and functions
- Constants: `FB_ACCEL_SMI_LYNX`, `SCREEN_X_RES`, `SCREEN_Y_RES_PC`, `SCREEN_Y_RES_NETBOOK`, `SCREEN_BPP`, `dac_reg`, and `dac_val`.
- External register base: `extern void __iomem *smtc_regbaseaddress`.
- MMIO byte access macros: `smtc_mmiowb()` and `smtc_mmiorb()`.
- Indexed register helpers: `smtc_crtcw()`, `smtc_grphw()`, `smtc_attrw()`, `smtc_seqw()`, and `smtc_seqr()`.
- Mode table shape: `struct modeinit` with arrays for SR, GR, AR, and CR register ranges.
- Endian helpers: `pal_rgb()`, `big_addr`, `mmio_addr`, `seqw17()`, `big_pixel_depth()`, and `big_swap()`.

## Control flow
This header is included by `sm712fb.c`; it does not register anything independently. The main driver sets `smtc_regbaseaddress` after mapping the device BAR, then all helper calls write VGA-compatible indexed registers by writing an index port and a data port relative to that MMIO base. Attribute writes perform the standard flip-flop reset by reading `0x3da`, write the attribute index to `0x3c0`, read `0x3c1`, then write the value to `0x3c0`.

## State and persistence behavior
The only state reference is the global `smtc_regbaseaddress`, owned by the `.c` file and used by all macros. `struct modeinit` instances are immutable table entries in `sm712fb.c` and encode full register programming sequences for each supported mode. Endian macros alter persistent framebuffer address layout and pseudo-palette byte order on big-endian builds.

## Dependencies and integration points
The header assumes Linux MMIO helpers (`readb()`/`writeb()`), fbdev acceleration constants, and the SM7xx driver's global mapping. It has no include guards in the shown file, relying on single inclusion by `sm712fb.c`. It directly encodes legacy VGA port offsets in MMIO form and integrates with the mode table writer in `sm7xx_set_timing()`.

## Risks
The macros depend on a valid non-NULL `smtc_regbaseaddress`; any call before mapping or after unmap would access invalid I/O memory. Global register base state prevents multiple devices from being isolated cleanly. The big-endian `big_swap(p)` macro lacks parentheses around shifted operands in a way that can be surprising and should be reviewed before reuse. The header has no guard, so accidental multiple inclusion could create duplicate inline definitions in unusual build contexts.

## Test signals
Useful validation is indirect through `sm712fb.c`: mode programming should produce expected SR/GR/AR/CR writes, palette programming should hit DAC registers, big-endian builds should select alternate `mmio_addr`/`big_addr`/word-swap behavior, and remove paths should stop using helpers after the global base is cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712fb.c

## Purpose
`sm712fb.c` is a PCI fbdev driver for Silicon Motion SM710, SM712, and SM720 display chips. It maps the device framebuffer/MMIO BAR, probes VRAM size, chooses a fixed mode from command-line VESA IDs or platform defaults, writes large static VGA register tables to program timings, exposes truecolor/pseudocolor fbdev operations, implements custom read/write paths for endian conversion, and provides basic PCI suspend/resume.

## Important APIs, types, and functions
- State types and defaults: `struct smtcfb_screen_info`, `struct smtcfb_info`, `smtcfb_var`, `smtcfb_fix`, `struct vesa_mode`, `vesa_mode_table[]`, and the large `vgamode[]` register table.
- Setup and color: `sm7xx_vga_setup()`, `sm712_setpalette()`, `chan_to_field()`, `smtc_setcolreg()`, and `smtc_blank()`.
- I/O and mode programming: `smtcfb_read()`, `smtcfb_write()`, `sm7xx_set_timing()`, `smtc_set_timing()`, `smtcfb_setmode()`, `smtc_check_var()`, and `smtc_set_par()`.
- Resource/lifecycle helpers: `smtc_map_smem()`, `smtc_unmap_smem()`, `sm7xx_init_hw()`, `sm7xx_vram_probe()`, `sm7xx_resolution_probe()`, `smtcfb_pci_probe()`, and `smtcfb_pci_remove()`.
- PM and module registration: `smtcfb_pci_suspend()`, `smtcfb_pci_resume()`, `SIMPLE_DEV_PM_OPS`, `smtcfb_driver`, `sm712fb_init()`, and `sm712fb_exit()`.

## Control flow
Module init rejects disabled modesetting, parses `video=sm712fb:` options, maps recognized VESA strings like `0x317` into `smtc_scr_info`, and registers the PCI driver. Probe removes conflicting firmware framebuffer apertures, enables the PCI function, requests BAR 0, allocates `fb_info` plus `smtcfb_info`, initializes fbops/fix/var/palette, wakes the chip, probes revision and VRAM, maps SM710/712 or SM720 memory layouts, sets chip-specific clocks and PCI-burst registers, selects resolution, maps screen memory, clears VRAM, and registers the framebuffer. `set_par` calls `smtcfb_setmode()`, which adjusts line length and RGB bitfields for 8/16/24/32 bpp, stores width/height/hz, and calls `sm7xx_set_timing()`. The timing writer searches `vgamode[]` for an exact width/height/bpp/60Hz match and writes sequencer, graphics, attribute, CRTC, and video-processor registers.

## State and persistence behavior
Per-device state in `struct smtcfb_info` stores PCI device, fb pointer, chip id/revision, mapped linear framebuffer and register windows, selected dimensions, and a 17-entry pseudo-palette. Global `smtc_regbaseaddress` backs the register helpers from `sm712.h`. `smtc_scr_info` stores boot-option-selected resolution/depth globally. Suspend writes sequencer registers to put memory in self-refresh and disables function blocks, then marks fbdev suspended under `console_lock()`. Resume reinitializes hardware clocks/registers by chip family, re-applies mode programming with `smtcfb_setmode()`, and clears fbdev suspend. Framebuffer contents are not explicitly saved by the driver.

## Dependencies and integration points
The driver depends on PCI, aperture removal, fbdev core, generic IOMEM drawing/mmap helpers, console locking, usercopy, and the local `sm712.h` register helper/mode layout. It supports PCI IDs `0x126f:0x710`, `0x126f:0x712`, and `0x126f:0x720`. The accepted user-facing mode input is VESA BIOS-style IDs in `vesa_mode_table[]`, not arbitrary fb mode strings. On MIPS, default height changes to 1024x600 for Loongson netbook panels.

## Risks
Mode support is static: if `check_var` accepts a resolution/depth with no matching `vgamode[]` entry, `sm7xx_set_timing()` silently writes only the common trailing registers after no table match. SM710/712 VRAM probing assumes 4 MiB and notes that 2 MiB SM712 systems may crash. `smtc_regbaseaddress` is global, making multi-device use unsafe. The SM720 screen-base offset adjustment in unmap subtracts from `screen_base`, which must still correspond to the mapped base. Custom read/write loops operate in 32-bit chunks even for unaligned byte counts and rely on over-read-safe vmalloc/IOMEM access behavior. Suspend does not save VRAM contents.

## Test signals
Tests should cover each supported PCI ID, 8/16/24/32 bpp modes from VESA IDs, default PC and MIPS netbook resolutions, static table lookup for every accepted resolution, palette writes in 8 bpp and pseudo-palette writes in truecolor modes, big-endian read/write and 32 bpp address shifting, framebuffer mmap/read/write correctness for odd byte counts, DPMS blank states, suspend/resume preserving a visible mode, and cleanup after failed map/register paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sm712fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/smscufx.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/smscufx.c

## Purpose
`smscufx.c` is a USB fbdev driver for SMSC UFX/UDX USB display controllers. It creates a virtual system-memory framebuffer, discovers monitor modes via EDID read over the device's I2C controller, configures clocks/DDR/display timings through vendor USB register requests, and sends damaged framebuffer rectangles to the device using bulk URBs. It is based on udlfb-style damage reporting and supports both fb_deferred_io and explicit damage ioctls.

## Important APIs, types, and functions
- State and transfer types: `struct dloarea`, `struct urb_node`, `struct urb_list`, and `struct ufx_data`.
- USB register/control helpers: `ufx_reg_read()`, `ufx_reg_write()`, `ufx_reg_clear_and_set_bits()`, `ufx_lite_reset()`, `ufx_blank()`, `ufx_unblank()`, `ufx_disable()`, `ufx_enable()`, `ufx_config_sys_clk()`, `ufx_config_ddr2()`, `ufx_calc_pll_values()`, `ufx_config_pix_clk()`, and `ufx_set_vid_mode()`.
- Damage and fbdev paths: `ufx_raw_rect()`, `ufx_handle_damage()`, `ufx_dpy_deferred_io()`, `ufx_ops_ioctl()`, `ufx_ops_setcolreg()`, `ufx_ops_open()`, `ufx_ops_release()`, `ufx_ops_check_var()`, `ufx_ops_set_par()`, `ufx_ops_blank()`, `ufx_ops_damage_range()`, `ufx_ops_damage_area()`, and `ufx_ops_mmap()`.
- EDID/mode setup: `ufx_i2c_init()`, `ufx_i2c_configure()`, `ufx_i2c_wait_busy()`, `ufx_read_edid()`, `ufx_setup_modes()`, `ufx_is_valid_mode()`, and `ufx_var_color_format()`.
- USB lifecycle and URBs: `ufx_usb_probe()`, `ufx_usb_disconnect()`, `ufx_alloc_urb_list()`, `ufx_get_urb()`, `ufx_submit_urb()`, `ufx_urb_completion()`, and `ufx_free_urb_list()`.

## Control flow
Probe allocates `ufx_data`, initializes two krefs, stores USB interface data, allocates a bounded pool of coherent bulk URBs, allocates `fb_info`, initializes cmap/modelist/fbops, reads device revision registers, resets the chip, configures system clock, DDR2, and I2C, reads EDID and selects a valid mode, enables the graphics engine, marks USB active, sets the video mode, and registers the framebuffer. Normal drawing updates system memory through generated deferred sysmem ops; damage callbacks or legacy `UFX_IOCTL_REPORT_DAMAGE` convert dirty rectangles into line-bounded raw rectangle commands and submit them over endpoint 1. Each bulk URB is removed from a semaphore-protected free list, filled, submitted, and returned by completion. Disconnect marks the device virtualized, stops USB traffic, frees framebuffer state immediately if no clients are open, drains URBs, unregisters the framebuffer, and defers final `ufx_data` freeing until krefs drop.

## State and persistence behavior
`struct ufx_data` persists USB handles, fb_info, URB pool, open count, kref, EDID cache, pseudo-palette, virtualized flag, `usb_active`, and `lost_pixels`. The framebuffer itself is vmalloc-backed `info->screen_buffer`; `fix.smem_start` is the virtual address used by damage packing. EDID is cached after a successful read and reused if later reads fail. On disconnect, existing clients can continue to write the virtual framebuffer but `usb_active=0` prevents new USB transfers; state is freed on last release. `fb_defio` is lazily allocated on open and cleaned up when the open count reaches zero, and explicit damage ioctl clients stretch the defio delay to effectively disable page-fault tracking until release or set_par resets it.

## Dependencies and integration points
The driver integrates with the USB core for probe/disconnect, vendor control messages, coherent bulk URBs, and endpoint 1 writes. It uses fbdev core, generated deferred sysmem ops, fb_deferred_io, EDID and VESA modelist helpers, vmalloc-backed mmap, usercopy ioctls, krefs, semaphores, spinlocks, delayed work, and module parameters `console` and `fb_defio`. It exposes legacy ioctls `UFX_IOCTL_RETURN_EDID` and `UFX_IOCTL_REPORT_DAMAGE` for DisplayLink-era userspace.

## Risks
`ufx_reg_read()` converts and dereferences the buffer even if `usb_control_msg()` failed, so callers receive stale/untrusted data on errors. `ufx_raw_rect()` copies from `(char *)info->fix.smem_start`, relying on that field being a CPU virtual pointer rather than a bus address. Damage ioctl clamps `x` and `y` but not `w`/`h` before calling `ufx_handle_damage()`, so invalid sizes return errors that the ioctl ignores. `lost_pixels` is set on URB errors/timeouts but no automatic full-screen recovery path is visible. Disconnect ordering virtualizes and possibly frees framebuffer data before `unregister_framebuffer(info)`, so lifetime depends on open count and krefs being balanced. The PLL search is brute-force and may leave zeroed values if no closer candidate is found.

## Test signals
High-value tests include USB probe with valid and failed register reads, EDID success/fallback/no-monitor paths, modelist filtering above 2048x1152 and too-fast pixel clocks, framebuffer realloc for largest selected mode, fbcon open rejection unless `console=1`, mmap with and without defio, explicit damage ioctl disabling defio delay, rectangle splitting across URB payload limits, URB timeout/completion/free races, disconnect with active fb clients, disconnect without clients, mode changes after open count returns to zero, blank/set_par reprogramming, and usercopy error handling for EDID/damage ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/smscufx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ssd1307fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/ssd1307fb.c

## Purpose
`ssd1307fb.c` is an I2C fbdev driver for Solomon SSD1305/SSD1306/SSD1307/SSD1309 OLED controllers. It exposes a 1 bpp monochrome framebuffer in system memory, uses deferred I/O to push updates to the OLED over I2C, initializes panel-specific controller registers from firmware properties, manages optional reset GPIO, VBAT regulator, PWM, and backlight/contrast, and converts fbdev's row-linear bit layout into the controller's page-oriented column byte format.

## Important APIs, types, and functions
- Device data: `struct ssd1307fb_deviceinfo`, `struct ssd1307fb_par`, and `struct ssd1307fb_array`.
- I2C helpers: `ssd1307fb_alloc_array()`, `ssd1307fb_write_array()`, `ssd1307fb_write_cmd()`, `ssd1307fb_set_col_range()`, and `ssd1307fb_set_page_range()`.
- Update paths: `ssd1307fb_update_rect()`, `ssd1307fb_update_display()`, `ssd1307fb_defio_damage_range()`, `ssd1307fb_defio_damage_area()`, and `ssd1307fb_deferred_io()`.
- fbdev/backlight/lifecycle: `ssd1307fb_blank()`, generated deferred sysmem `ssd1307fb_ops`, `ssd1307fb_init()`, `ssd1307fb_update_bl()`, `ssd1307fb_get_brightness()`, `ssd1307fb_probe()`, and `ssd1307fb_remove()`.
- Match data: `ssd1307fb_ssd1305_deviceinfo`, `ssd1307fb_ssd1306_deviceinfo`, `ssd1307fb_ssd1307_deviceinfo`, `ssd1307fb_ssd1309_deviceinfo`, OF compatibles, and I2C IDs.

## Control flow
Probe allocates `fb_info` plus private state, reads match data, optional reset GPIO and VBAT regulator, and display properties such as width, height, offsets, precharge phases, lookup table, segment remap, COM layout, contrast timing, area-color, and low-power flags. It allocates zeroed page memory sized as `DIV_ROUND_UP(width, 8) * height`, creates deferred I/O state with a delay derived from the `refreshrate` module parameter, fills fbops/fix/var/screen fields, resets and powers the panel, initializes the controller command sequence, registers a backlight device, and finally registers the framebuffer. Updates come through deferred sysmem operations or full deferred I/O; rectangles are converted page-by-page and sent as I2C data arrays after cached column/page range programming.

## State and persistence behavior
`struct ssd1307fb_par` stores all controller configuration, cached column/page ranges, resource pointers, and current contrast. `info->screen_buffer` is normal memory allocated with `__get_free_pages()` and `info->fix.smem_start` is set to its physical address. The display contents are persistent in system memory and mirrored to the controller on deferred updates; no suspend-specific save path exists beyond backlight ops using `BL_CORE_SUSPENDRESUME`. Cached range fields avoid repeated column/page commands when consecutive updates use the same range. Remove blanks the display, unregisters backlight and fbdev, disables PWM/regulator, cleans up deferred I/O, frees pages, and releases `fb_info`.

## Dependencies and integration points
The driver integrates with the I2C core, fbdev core, generated deferred sysmem ops, fb_deferred_io, firmware property APIs, optional GPIO, optional regulator, optional PWM for SSD1307, and Linux backlight core. OF match data supplies controller-specific defaults for VCOMH, clock divider/frequency, PWM requirement, and charge pump requirement. User-visible behavior is controlled partly by device properties under the `solomon,*` namespace and module parameter `refreshrate`.

## Risks
`ssd1307fb_update_rect()` assumes the requested rectangle is within bounds; generated damage callbacks should provide sane regions, but direct misuse could overrun conversion logic. A `refreshrate` value of zero would make `HZ / refreshrate` invalid during probe. PWM cleanup calls `pwm_disable()`/`pwm_put()` even on controllers that do not require PWM or before `pwm_get()` succeeds, depending on pointer state. `ssd1307fb_write_array()` returns the positive short-write byte count rather than normalizing all short writes to a negative errno. Deferred range damage currently triggers full-display update for range writes, which is simple but inefficient on slow I2C panels.

## Test signals
Tests should cover all four compatibles and I2C IDs, default and property-overridden geometry/offsets/timings, reset GPIO pulse, optional VBAT regulator paths, SSD1307 PWM requirement, lookup table validation, contrast updates through backlight, blank/unblank commands, full-screen and partial rectangle updates including unaligned y/height crossing page boundaries, deferred mmap/write drawing, invalid or zero `refreshrate`, I2C short write/error propagation, and remove cleanup after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ssd1307fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sstfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sstfb.c

## Purpose
`sstfb.c` is a PCI fbdev driver for 3dfx Voodoo Graphics and Voodoo2 boards. It maps the Voodoo MMIO and linear framebuffer windows, detects attached RAMDAC type, programs graphics/video PLLs, validates and applies 16 bpp display modes, manages VGA pass-through, detects framebuffer memory size, exposes basic fbdev IOMEM operations and a small ioctl/sysfs control surface, and shuts the board down on removal.

## Important APIs, types, and functions
- Module options and hardware tables: `vgapass`, `mem`, `clipping`, `gfxclk`, `slowpci`, `mode_option`, `voodoo_spec[]`, and `dacs[]`.
- MMIO/DAC helpers: `__sst_read()`, `__sst_write()`, `__sst_set_bits()`, `__sst_unset_bits()`, `__sst_wait_idle()`, `__sst_dac_read()`, `__sst_dac_write()`, `__dac_i_read()`, and `__dac_i_write()`.
- Timing and mode functions: `sst_calc_pll()`, `sstfb_check_var()`, `sstfb_set_par()`, `sstfb_setcolreg()`, and `sstfb_clear_screen()`.
- VGA pass-through and userspace controls: `sstfb_setvgapass()`, `store_vgapass()`, `show_vgapass()`, and `sstfb_ioctl()`.
- Hardware detection/init: `sst_get_memsize()`, `sst_detect_att()`, `sst_detect_ti()`, `sst_detect_ics()`, `sst_set_pll_att_ti()`, `sst_set_pll_ics()`, `sst_set_vidmod_att_ti()`, `sst_set_vidmod_ics()`, `sst_detect_dactype()`, `sst_init()`, and `sst_shutdown()`.
- PCI lifecycle: `sstfb_probe()`, `sstfb_remove()`, `sstfb_init()`, `sstfb_exit()`, and `sstfb_id_tbl`.

## Control flow
Module init parses `video=sstfb:` options, updates global behavior flags and initial mode string, and registers the PCI driver. Probe removes conflicting firmware apertures, enables PCI, allocates `fb_info` with `struct sstfb_par`, records Voodoo1/Voodoo2 type, reserves and maps the 4 MiB MMIO and framebuffer windows, runs `sst_init()` to reset the board, remap DAC access, detect the DAC, set the graphics clock, initialize FBI registers, and enable the video clock. It then detects usable framebuffer size, selects and validates a mode through `fb_find_mode()`/`sstfb_check_var()`, programs the mode with `sstfb_set_par()`, allocates a colormap, registers fbdev, clears the screen, and optionally creates the `vgapass` sysfs file. Runtime `set_par` resets video/FBI/FIFO, writes timing registers, programs the DAC video mode and PLL, restores FBI registers, configures tile counts, enables DRAM refresh, selects 565 LFB mode, and optionally enables clipping.

## State and persistence behavior
Private state in `struct sstfb_par` comes from `video/sstfb.h` and includes PCI device, board type/revision, MMIO base, current PLL timing, DAC switch table, palette, VGA pass-through state, and computed timing/tile fields. Global module parameters persist policy across devices. `sst_get_memsize()` writes test patterns into framebuffer memory to infer 1/2/4 MiB unless the `mem` option forces a value. The pseudo-palette stores up to 16 truecolor entries; no hardware CLUT is programmed for 16 bpp. Remove calls `sst_shutdown()` to reset video/gfx/fifo, drop DRAM refresh, set a low graphics clock, enable VGA pass-through, disable video clock, then unmaps resources and unregisters fbdev.

## Dependencies and integration points
The driver depends on PCI IDs for `PCI_DEVICE_ID_3DFX_VOODOO` and `PCI_DEVICE_ID_3DFX_VOODOO2`, aperture removal, fbdev IOMEM helpers, mode database, usercopy, sysfs under `CONFIG_FB_DEVICE`, and register definitions/types from `video/sstfb.h`. It exposes ioctls `SSTFB_SET_VGAPASS` and `SSTFB_GET_VGAPASS`, module options for memory size/VGA pass-through/clipping/gfx clock/PCI speed/mode, and a sysfs `vgapass` attribute.

## Risks
`__sst_wait_idle()` is an unbounded busy loop; stuck hardware can hang the CPU. Failure during `sst_init()` can leave hardware in a reset/remapped state, which the comments acknowledge. Only 16 bpp is supported despite comments about legacy 24/32 bpp, and Voodoo1 rejects interlace/doublescan. Memory detection writes directly to framebuffer offsets and may disturb visible contents. Forced `gfxclk` is explicitly dangerous if out of spec. Resource cleanup on probe failure returns `-ENXIO` regardless of original failure. Clipping disabled can make offscreen writes wrap unpredictably. There is no suspend/resume support.

## Test signals
Relevant tests include Voodoo1 and Voodoo2 probe on known DAC variants (TI, AT&T, ICS), invalid DAC detection handling, PLL calculation across default and selected modes, rejection of unsupported bpp/timings/resolutions, Voodoo2 interlace/doublescan handling, memory-size autodetect and forced `mem`, `vgapass` ioctl/sysfs/module option behavior, clipping on/off framebuffer writes near screen boundaries, big-endian LFB swizzle, failed resource-map cleanup, remove shutdown leaving VGA pass-through usable, and stress around hardware idle waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sstfb.c -->
