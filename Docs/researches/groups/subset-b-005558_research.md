# subset-b-005558 Research

Grouped source research for legacy fbdev Cirrus/PowerMac/Cobalt/CLPS711x drivers and the fbdev core helpers covering character-device access, deferred I/O, packed-pixel drawing, logos, cmap, DDC, command-line options, backlight notification, and build configuration. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cirrusfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cirrusfb.c

## Purpose

This file implements the legacy accelerated fbdev driver for Cirrus Logic VGA chipsets on PCI and Amiga Zorro boards. It supports multiple board families, including SD64, Piccolo, Picasso, Spectrum, Picasso IV, Alpine/GD543x, GD5480, and Laguna/GD546x variants. The complete 2954-line source was read.

## Important APIs, Types, and Functions

The main private type is `struct cirrusfb_info`, which stores register bases, optional Laguna MMIO, board type, special-function-register shadow, mode flags, blanking state, pseudo-palette, and an unmap callback. The driver exposes `struct fb_ops cirrusfb_ops` with open/release, I/O-memory read/write/mmap helpers, `cirrusfb_check_var()`, `cirrusfb_set_par()`, `cirrusfb_setcolreg()`, `cirrusfb_pan_display()`, `cirrusfb_blank()`, accelerated fill/copy/imageblit, and `cirrusfb_sync()`.

Important internal helpers include `init_vgachip()`, `cirrusfb_set_par_foo()`, `cirrusfb_check_pixclock()`, `cirrusfb_check_mclk()`, `bestclock()`, `switch_monitor()`, `WGen()`, `RGen()`, `AttrOn()`, `WHDR()`, `WSFR()`, `WClut()`, `cirrusfb_WaitBLT()`, `cirrusfb_BitBLT()`, and `cirrusfb_RectFill()`. Bus integration is via `cirrusfb_pci_driver` and `cirrusfb_zorro_driver`.

## Control Flow

Module/init setup honors `fb_modesetting_disabled("cirrusfb")`, parses `video=cirrusfb:` options when built in, and registers PCI and/or Zorro drivers according to configuration. PCI probe removes conflicting apertures, enables the device, allocates `fb_info`, classifies board type from the PCI ID table, maps display memory and optional Laguna MMIO, probes video RAM size, reserves legacy VGA ports when available, then calls `cirrusfb_register()`. Zorro probe locates register and RAM resources from board-specific `zorrocl` descriptors, handles split/optional Picasso IV RAM, maps Zorro II direct or Zorro III ioremap addresses, initializes SR1F where required, then registers the framebuffer.

Registration fills `fb_info` and `fix` fields, allocates a 256-entry cmap, finds the initial mode with `fb_find_mode()`, validates it, and calls `register_framebuffer()`. Mode setting runs through `cirrusfb_check_var()` and then `cirrusfb_set_par()`, which intentionally writes the hardware mode twice. The mode write path computes CRTC timings, clock numerator/denominator/divider, multiplexing/double-VCLK state, board-specific sequencer and hidden-DAC settings, line pitch, screen-start extension bits, Laguna format/threshold registers, and finally enables display sequencing. Pan display converts x/y offsets into the Cirrus split start-address registers. Acceleration paths clip requested rectangles, fall back to generic `cfb_*` helpers when disabled or unsupported, and otherwise program the Cirrus blitter registers.

## State and Persistence Behavior

Driver state is held in `fb_info`, `cirrusfb_info`, `opencount`, module parameters `noaccel` and `mode_option`, and bus drvdata. Hardware-visible state includes VGA sequencer, graphics, CRTC, attribute, DAC, hidden DAC, special function, and Laguna MMIO registers, plus framebuffer memory. Zorro monitor switching uses the `SFR` shadow and a static `IsOn` flag in `switch_monitor()`. No file-backed persistence exists, but module parameters and boot command-line options affect initial state.

## Dependencies and Integration Points

The file depends on fbdev core APIs, generic I/O-memory fbops macros, VGA/Cirrus register definitions, PCI, aperture conflict removal, Zorro, Amiga hardware helpers, and optional debug dumps. It integrates with `/dev/fb*`, fbcon, module autoloading through PCI/Zorro tables, boot video options, and generic `cfb_fillrect()`, `cfb_copyarea()`, and `cfb_imageblit()` fallback routines.

## Risks and Edge Cases

This is register-heavy legacy hardware code with many board-specific assumptions. Risks include unsupported 32 bpp despite some internal 32 bpp blitter paths, truncated offsets in `check_var()` when virtual dimensions equal visible dimensions, wait loops that spin indefinitely if the blitter never clears busy bits, and a global `opencount`/Zorro monitor switch state that is not per-device. The PCI path sets `regbase` to `NULL` for VGA-style register access and maps `laguna_mmio`; `cirrusfb_pci_unmap()` checks `if (cinfo->laguna_mmio == NULL) iounmap(cinfo->laguna_mmio)`, which appears inverted and risks leaking non-NULL mappings while calling `iounmap(NULL)` on the NULL case. Acceleration clips a copied `modded` rectangle but passes original coordinates/sizes to the blitter, so clipped requests near edges require careful review. Several comments mark incomplete Picasso IV and 24 bpp acceleration behavior.

## Test Signals

Useful tests include PCI probe/remove for each supported PCI ID, Zorro probe/remove with contiguous and non-contiguous RAM, boot parameter parsing for `mode:` and `noaccel`, fbcon rendering at 1/8/16/24 bpp, pan/blank/setcolreg ioctls, mode rejection for oversized virtual screens and vertical totals, blitter fill/copy/image paths with generic fallback, forced busy blitter timeouts under instrumentation, aperture conflict handling, and suspend-like blank/unblank cycles. Build coverage should include PCI-only, Zorro-only, both enabled, and non-module built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cirrusfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/clps711x-fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/clps711x-fb.c

## Purpose

This platform driver provides fbdev support for the Cirrus Logic CLPS711X/EP7209 LCD controller. It programs the LCD controller registers, framebuffer start address, grayscale palette, syscon LCD enable bit, and optional LCD regulator. The complete 374-line source was read.

## Important APIs, Types, and Functions

Private state lives in `struct clps711x_fb_info`, containing the LCD clock, controller MMIO base, syscon regmap, framebuffer size, native display mode, optional regulator, AC prescale, and colormap inversion flag. `clps711x_fb_ops` implements `clps711x_fb_setcolreg()`, `clps711x_fb_check_var()`, `clps711x_fb_set_par()`, and a no-op blank method using default I/O-memory fbops. LCD class integration is through `clps711x_lcd_ops`, `clps711x_lcd_get_power()`, and `clps711x_lcd_set_power()`.

## Control Flow

Probe exits early if `video=clps711x-fb:off` disables the driver. It allocates `fb_info`, maps controller and framebuffer resources, requires framebuffer physical alignment to 256 MiB, obtains the clock and syscon regmap, reads the `display` phandle, converts the native timing to `fb_videomode`, reads `ac-prescale`, `cmap-invert`, and `bits-per-pixel`, then disables the LCD if the current hardware start address does not match the resource. If LCD is disabled, it writes the framebuffer base nibble and clears framebuffer memory. It then obtains the optional `lcd` regulator, initializes fb metadata, allocates a 16-entry cmap, applies the mode through `fb_set_var()`, registers an LCD class device, and finally registers the framebuffer.

Mode validation accepts 1 through 4 bpp and checks the LCDCON width and framebuffer-size fields. Mode setting computes line length, `smem_len`, LCDCON frame length, horizontal size, AC prescale, pixel prescaler from clock rate and pixclock, grayscale enable/mode bits, disables the LCD, writes LCDCON, then re-enables the LCD.

## State and Persistence Behavior

State is in `fb_info`, `clps711x_fb_info`, LCDCON/PALLSW/PALMSW/FBADDR registers, syscon `SYSCON1_LCDEN`, and the regulator enable state. The framebuffer memory is cleared on probe only when the controller is not already using the same framebuffer address. There is no persistent storage, but device-tree properties determine startup behavior.

## Dependencies and Integration Points

The file depends on platform-device resources, devm MMIO mapping, clock framework, syscon/regmap, CLPS711X syscon definitions, regulator framework, OF display timings, LCD class devices, and fbdev core registration. Device-tree binding uses compatible `cirrus,ep7209-fb`, a `display` phandle, `bits-per-pixel`, optional `ac-prescale`, optional `cmap-invert`, and optional `lcd` regulator.

## Risks and Edge Cases

Risks include integer truncation in byte-size calculations for non-byte-aligned 1/2/4 bpp modes, strict 256 MiB physical address alignment, optional regulator handling where non-defer errors are tolerated as absent, and no real `fb_blank()` implementation beyond the LCD class power hook. The `clps711x_fb_setcolreg()` inversion path computes `0xf - level` after `level` has already been shifted into position, which is only intuitive for low-index shifts and should be verified against hardware palette layout. The unreachable `unregister_framebuffer(info);` line after a successful return is dead code.

## Test Signals

Test with DT-provided timings at 1, 2, and 4 bpp; invalid bpp and invalid pixclock rejection; syscon LCD enable transitions around `set_par`; framebuffer alignment failure; regulator defer and enable/disable paths; palette writes with and without `cmap-invert`; probe/remove leak checks; and fbcon or userspace writes confirming grayscale output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/clps711x-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cobalt_lcdfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cobalt_lcdfb.c

## Purpose

This platform driver exposes a small Cobalt/SEAD3 character LCD as an fbdev text framebuffer. It maps LCD control/data registers, implements reads and writes over the LCD text address space, controls blanking and cursor position, and registers a 16x2 text framebuffer. The complete 350-line source was read.

## Important APIs, Types, and Functions

Important helpers are `lcd_write_control()`, `lcd_read_control()`, `lcd_write_data()`, `lcd_read_data()`, `lcd_busy_wait()`, and `lcd_clear()`. `cobalt_lcd_fbops` implements `fb_read`, `fb_write`, `fb_blank`, `fb_cursor`, default I/O-memory drawing helpers, and default mmap. The fixed screen description is `cobalt_lcdfb_fix`, with `FB_TYPE_TEXT`, `FB_AUX_TEXT_MDA`, mono visual, and 16-character line length.

## Control Flow

Probe allocates a bare `fb_info`, maps the single MMIO resource, populates fixed fields, registers the framebuffer, stores drvdata, clears/resets the LCD, and logs device registration. Reads clamp `ppos` and `count` to 32 LCD character positions, then for each character wait for not-busy, program the text cursor address, wait again, read data, and translate the 16-character first row to the second row by jumping from `0x0f` to `0x40`. Writes follow the same addressing flow but copy data from userspace first and write each byte. Blanking waits for not-busy and sends `LCD_ON` for unblank or `LCD_OFF` otherwise. Cursor handling supports only `FB_CUR_SETPOS`, validates 16x2 coordinates, writes cursor position, waits, then enables or disables the cursor.

## State and Persistence Behavior

The driver has almost no private state beyond `fb_info` and the MMIO mapping. The LCD controller stores the displayed characters, cursor address, busy bit, and on/off/cursor mode. File offsets (`ppos`) are maintained by the VFS caller. There is no persistent storage and no software shadow buffer of the LCD contents.

## Dependencies and Integration Points

The file depends on platform-device resources, devm I/O remapping, fbdev core, userspace copy helpers, sleep/udelay timing, signal handling, and the LCD controller's register protocol. Userspace integration is through `/dev/fb*` reads/writes and cursor/blank ioctls.

## Risks and Edge Cases

Read/write operations can return partial lengths when busy wait fails. `lcd_busy_wait()` sleeps interruptibly and maps an interrupted wait to `-EINTR`; the read/write wrappers convert that to `-ERESTARTSYS` only if a signal is pending. There is no explicit locking around register cursor/data access, so concurrent readers/writers/cursor updates can interleave LCD address programming. The framebuffer is text-like, so generic drawing or mmap users may not behave like pixel-framebuffer clients expect. Probe clears the LCD only after registration, allowing a very small window where userspace could access an uncleared device.

## Test Signals

Test platform probe/remove, 0-byte and out-of-range reads/writes, row wrap from offset 15 to 0x40, partial reads/writes under injected busy timeouts, signal interruption during busy wait, blank/unblank commands, cursor set/enable/disable with valid and invalid coordinates, and concurrent read/write stress for register sequencing issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cobalt_lcdfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.c

## Purpose

This file implements fbdev support for the PowerMac "control" display adapter. It discovers the Open Firmware node, maps framebuffer/control/cmap registers, probes installed VRAM banks, chooses a Mac video mode and color depth, programs timing/RADACAL/clock registers, and exposes pan/blank/mmap/color operations. The complete 1018-line source was read.

## Important APIs, Types, and Functions

Private state is split between `struct fb_par_control`, which represents a desired/applied mode, and `struct fb_info_control`, which embeds `struct fb_info` and tracks cmap registers, control registers, framebuffer mapping, VRAM bank selection, total VRAM, and cached pseudo-palette. Key functions include `controlfb_setcolreg()`, `set_control_clock()`, `set_screen_start()`, `control_set_hardware()`, `find_vram_size()`, `read_control_sense()`, `calc_clock_params()`, `control_var_to_par()`, `control_par_to_var()`, `controlfb_check_var()`, `controlfb_set_par()`, `controlfb_pan_display()`, `controlfb_blank()`, `controlfb_mmap()`, `control_setup()`, `init_control()`, `control_of_init()`, and `control_init()`.

## Control Flow

`device_initcall(control_init)` parses `video=controlfb:` options, finds the `control` OF node, and calls `control_of_init()`. OF init enforces a single global instance, obtains framebuffer and register resources, maps the big-endian framebuffer aperture and control registers, maps a hard-coded RADACAL cmap register page, probes VRAM banks, then calls `init_control()`. Initialization chooses cmode/vmode from boot options, NVRAM, or monitor sense fallback, initializes `fb_info`, computes virtual height from VRAM, applies the selected mode with `fb_set_var()`, and registers the framebuffer.

Mode conversion aligns horizontal resolution, virtual width, and x offset to 32-byte hardware boundaries, chooses mode/radacal values by color depth and VRAM size, validates memory footprint including `CTRLFB_OFF`, computes CUDA clock parameters and sixteen timing registers, and maps fb var fields back to normalized values. Hardware programming turns display off, sends clock parameters via CUDA IIC when available, writes RADACAL registers, writes vertical/horizontal timing registers, pitch/mode/vram/start/refresh/intr registers, then turns the display on. Pan display only updates start address if bounds pass. Mmap maps framebuffer cached write-through and optional MMIO noncached only when acceleration flags allow it.

## State and Persistence Behavior

State includes a global `control_fb`, `default_vmode`, `default_cmode`, current `p->par`, pseudo-palette entries, VRAM bank/attribute state, and mapped resource metadata. Hardware-visible state includes display control/timing registers, RADACAL color/clock settings, monitor sense lines, framebuffer start address, and VRAM bank select. NVRAM is read for default video mode/color mode if reachable; the driver does not write persistent settings.

## Dependencies and Integration Points

The driver is specific to 32-bit PowerMac/PPC behavior but compiles stubs for some accessors when unavailable. It depends on Open Firmware address translation, PCI resource layout, NVRAM, ADB CUDA for clock programming, `macmodes.c` helpers, BootX text update hooks, fbdev core, and architecture cache/pgprot functions. It integrates with fbcon through `register_framebuffer()`, pan/blank ioctls, and palette operations.

## Risks and Edge Cases

Risks include single-device global state, hard-coded cmap physical address `0xf301b000`, direct VRAM write probes that assume non-existent banks ignore writes, architecture-specific cache invalidation, and `control_set_hardware()` avoiding full reprogramming when only offsets differ. CUDA clock setting is compiled out without `CONFIG_ADB_CUDA`, so timing can depend on firmware defaults. `controlfb_setcolreg()` populates pseudo-palette entries from the register number rather than the requested RGB values for direct-color modes, which matches old code style but should be validated. Cleanup unregisters resources only on failed init or never-registered teardown; there is no module exit because this is initcall-style built-in code.

## Test Signals

Test OF discovery failure, single-instance rejection, VRAM bank probing for 2 MiB bank 1, 2 MiB bank 2, and 4 MiB combinations, NVRAM/default/monitor-sense mode selection, fallback to 640x480x8, mode validation for 8/16/32 bpp and oversized virtual screens, pan alignment, blank modes, mmap framebuffer versus MMIO offsets, palette writes, CUDA clock programming, and BootX text update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.h

## Purpose

This header defines the hardware register layout, timing register value containers, framebuffer offset, and supported Mac mode/depth table used by `controlfb.c`. The complete 143-line source was read.

## Important APIs, Types, and Functions

`struct cmap_regs` models RADACAL colormap/misc register spacing. `struct preg` represents a padded 32-bit control register, and `struct control_regs` lays out the vertical timing, horizontal timing, control, start address, pitch, monitor sense, VRAM, mode, refresh, and interrupt registers. `struct control_regints` is the unpacked timing view, while `struct control_regvals` stores the 16 timing values plus mode, RADACAL control, and three clock parameters. `CTRLFB_OFF` defines the 16-byte offset of pixel zero in framebuffer memory. `control_mac_modes[]` maps Mac video modes to the maximum supported color mode for 2 MiB and 4 MiB VRAM configurations.

## Control Flow

There is no executable control flow in the header. The layout directly drives `controlfb.c` register writes through `CNTRL_REG()` and determines mode fallback logic in `init_control()`.

## State and Persistence Behavior

The header stores no runtime state, but its static `control_mac_modes[]` table becomes compiled data in each translation unit that includes it. Its register structs define how driver state maps onto hardware-visible MMIO.

## Dependencies and Integration Points

The header is tightly coupled to PowerMac "control" hardware, `macmodes.c` mode IDs, and `controlfb.c` timing calculations. The exact padding values are part of the MMIO ABI between the C structs and the device register spacing.

## Risks and Edge Cases

Because `control_mac_modes[]` is defined `static` in a header, including it from multiple C files would duplicate data; currently it is used by `controlfb.c`. Register layout mistakes would cause broad hardware misprogramming. Comments note uncertainty for horizontal timing units above 1024/1280 pixels, which is relevant for high-resolution modes in the table.

## Test Signals

Validation is mostly build and hardware driven: ensure `controlfb.c` compiles with this header, verify register offsets against known hardware documentation, and exercise every `control_mac_modes[]` entry that claims support for 2 MiB or 4 MiB VRAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/controlfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Kconfig

## Purpose

This Kconfig file defines fbdev core configuration symbols for the framebuffer core, legacy `/dev/fb*` device support, DDC, generic drawing helpers, endian handling, system/I/O memory file operations, deferred I/O, helper bundles, backlight notification, mode helpers, and tile blitting. The complete 207-line source was read.

## Important APIs, Types, and Functions

Key symbols include `FB_CORE`, `FB_NOTIFY`, `FB_DEVICE`, `FB_DDC`, `FB_CFB_FILLRECT`, `FB_CFB_COPYAREA`, `FB_CFB_IMAGEBLIT`, `FB_CFB_REV_PIXELS_IN_BYTE`, `FB_SYS_*`, `FB_PROVIDE_GET_FB_UNMAPPED_AREA`, `FB_FOREIGN_ENDIAN`, `FB_BOTH_ENDIAN`, `FB_BIG_ENDIAN`, `FB_LITTLE_ENDIAN`, `FB_SYSMEM_FOPS`, `FB_DEFERRED_IO`, `FB_DMAMEM_HELPERS`, `FB_IOMEM_FOPS`, `FB_IOMEM_HELPERS`, `FB_SYSMEM_HELPERS`, `FB_BACKLIGHT`, `FB_MODE_HELPERS`, and `FB_TILEBLITTING`.

## Control Flow

There is no runtime flow. Configuration selections control which objects from the core Makefile are built and which helper APIs are available to drivers. Helper bundle symbols select the appropriate drawing and file-operation modules.

## State and Persistence Behavior

The persistent state is the kernel configuration. It determines whether fbdev exists, whether userspace character-device/sysfs/procfs interfaces are available, whether deferred I/O and helper functions are compiled, and what endian conversion support generic drawing code includes.

## Dependencies and Integration Points

The file integrates with `drivers/video/fbdev/core/Makefile`, fbdev drivers selecting helper bundles, framebuffer console, I2C DDC support, backlight notification, EDID/mode helper users, and nommu mmap support.

## Risks and Edge Cases

Configuration risks include drivers selecting insufficient helper symbols, users expecting `/dev/fb*` when `FB_DEVICE=n`, foreign-endian combinations not matching hardware, and helper bundles silently pulling generic drawing modules. `FB_DEVICE` defaults to `FB` but is not required for framebuffer console, so userspace compatibility can differ from console behavior.

## Test Signals

Run focused `olddefconfig`, `allmodconfig`, `allyesconfig`, and minimal configs for core-only, no `FB_DEVICE`, I/O-memory helpers, system-memory helpers, deferred helper bundles, DDC, tileblitting, and foreign-endian choices. Build output should match the object mappings in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Makefile

## Purpose

This Makefile maps fbdev core Kconfig symbols to built-in and modular objects. It defines the aggregate `fb.o` composition and independently built helper modules for drawing, file operations, DDC, and svgalib. The complete 37-line source was read.

## Important APIs, Types, and Functions

`obj-$(CONFIG_FB_CORE) += fb.o` creates the core aggregate. `fb-y` always includes `fb_info.o`, `fbmem.o`, `fbcmap.o`, `modedb.o`, `fbcvt.o`, and `fb_cmdline.o`; additional objects include `fb_backlight.o`, `fbmon.o`, `fb_defio.o`, `fb_chrdev.o`, `fb_procfs.o`, `fbsysfs.o`, fbcon/rotation/logo objects, and optional tileblit. Standalone objects map `CONFIG_FB_CFB_*`, `CONFIG_FB_IOMEM_FOPS`, `CONFIG_FB_SYS_*`, `CONFIG_FB_SYSMEM_FOPS`, `CONFIG_FB_SVGALIB`, and `CONFIG_FB_DDC`.

## Control Flow

There is no runtime flow. Kbuild expands selected config symbols into object lists, links `fb.o`, and builds helper modules or built-ins depending on tristate settings.

## State and Persistence Behavior

No runtime state exists. The durable contract is build composition: exported APIs from these files are available only when their corresponding symbols are selected.

## Dependencies and Integration Points

The Makefile integrates with `core/Kconfig`, fbcon configuration, logo configuration, and drivers that call generic helper functions such as `cfb_fillrect()`, `fb_io_read()`, `fb_deferred_io_init()`, or `fb_ddc_read()`.

## Risks and Edge Cases

Risks are build drift: adding source files without Makefile entries, missing optional objects from `fb-y`, or helper symbols not matching exported APIs. Conditional `ifdef CONFIG_FB` adds `fb_backlight.o` and `fbmon.o` only when the broader fbdev config is active, which must remain aligned with Kconfig expectations.

## Test Signals

Build with core as built-in and module-like tristate helpers, framebuffer console on/off, logo on/off, rotation on/off, and each generic helper selected independently. Inspect generated object lists and exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/bitblit.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/bitblit.c

## Purpose

This file implements the standard pixel-based framebuffer-console bitblit operations. It adapts console character cells to fbdev `fb_copyarea`, `fb_fillrect`, `fb_imageblit`, and cursor operations for drivers using packed-pixel drawing. The complete 394-line source was read.

## Important APIs, Types, and Functions

Key functions are `update_attr()`, `bit_bmove()`, `bit_clear()`, `bit_putcs_aligned()`, `bit_putcs_unaligned()`, `bit_putcs()`, `bit_clear_margins()`, `bit_cursor()`, `bit_update_start()`, and `fbcon_set_bitops_ur()`. The exported behavior is through the local `struct fbcon_bitops bit_fbcon_bitops` assigned to `struct fbcon_par`.

## Control Flow

Fbcon selects these bitops for unrotated pixel consoles. Character movement maps cell coordinates to pixel rectangles and calls the driver copyarea operation. Clear maps cell rectangles to fillrect with the background color. `bit_putcs()` chunks glyphs into `info->pixmap`, applies underline/bold/reverse attributes when needed, handles byte-aligned and unaligned font widths, clips against visible x/y resolution, and submits a 1-bit `fb_image` to the driver. Cursor handling tracks cached cursor image, colors, position, size, hot spot, and mask in `fbcon_par`; it calls the driver cursor callback when available and falls back to `soft_cursor()` on error.

## State and Persistence Behavior

State is held in `fbcon_par` cursor caches, `info->pixmap`, and transient kmalloc buffers for attributed glyphs and cursor masks. There is no persistent storage. Console screen contents remain owned by the console layer, while this file translates them into framebuffer drawing calls.

## Dependencies and Integration Points

The file depends on fbcon internals, virtual console state, `scr_readw()`, font metadata, `fb_pad_aligned_buffer()`, `fb_pad_unaligned_buffer()`, `fb_get_buffer_offset()`, driver fbops, and soft cursor support. It is built into `fb.o` when `CONFIG_FRAMEBUFFER_CONSOLE=y`.

## Risks and Edge Cases

Risks include atomic allocation failures causing skipped glyph/cursor updates, reliance on driver `fb_imageblit()` clipping correctness after local clipping, attribute expansion overhead, handling high fonts through `vc_hi_font_mask`, and cursor cache lifetime around font changes. `bit_putcs()` computes `maxcnt = info->pixmap.size / cellsize`; malformed pixmap sizing or zero cellsize would be serious, though fbcon normally validates fonts.

## Test Signals

Exercise console scrolling, clear, margins, putcs with aligned and unaligned font widths, underline/bold/reverse attributes, high-font characters, cursor shape/position/color changes, hardware cursor failure fallback, panning update_start, and small pixmap chunking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/bitblit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbcopyarea.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbcopyarea.c

## Purpose

This file exports `cfb_copyarea()`, the generic I/O-memory packed-pixel area-copy helper for fbdev drivers without hardware copy acceleration. The complete 36-line source was read.

## Important APIs, Types, and Functions

The only runtime function is `cfb_copyarea(struct fb_info *p, const struct fb_copyarea *area)`. It includes `cfbmem.h` for I/O-memory access and `fb_copyarea.h` for the generic bit-copy implementation, with optional `FB_REV_PIXELS_IN_BYTE` enabled by `CONFIG_FB_CFB_REV_PIXELS_IN_BYTE`.

## Control Flow

The wrapper returns if the framebuffer is not running, warns once if the framebuffer is marked virtual rather than I/O memory, calls driver `fb_sync()` when present, then delegates to inline `fb_copyarea()`.

## State and Persistence Behavior

No independent state is kept. The helper reads and writes framebuffer memory and respects `fb_info` state and flags.

## Dependencies and Integration Points

It depends on fbdev core structures, I/O-memory accessors, optional bit reversal support, and the shared `fb_copyarea.h` engine. Drivers call it directly or through default I/O-memory helper macros.

## Risks and Edge Cases

Risks are mostly mismatched memory type flags and reliance on the header implementation for clipping, overlap direction, endian reversal, and bit alignment. Calling it on a virtual-memory framebuffer is warned but still attempted.

## Test Signals

Test area copies at multiple bpp values, overlapping forward/reverse copies, unaligned x offsets, reverse-pixel low-bpp modes, stopped framebuffer state, `fb_sync()` invocation, and warning behavior for `FBINFO_VIRTFB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbcopyarea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbfillrect.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbfillrect.c

## Purpose

This file exports `cfb_fillrect()`, the generic I/O-memory packed-pixel rectangle-fill helper for fbdev drivers. The complete 36-line source was read.

## Important APIs, Types, and Functions

The sole runtime API is `cfb_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`. It uses `cfbmem.h` and `fb_fillrect.h`, with optional reverse-pixel support through `CONFIG_FB_CFB_REV_PIXELS_IN_BYTE`.

## Control Flow

The wrapper checks `FBINFO_STATE_RUNNING`, warns once if the framebuffer is not I/O memory, calls `fb_sync()` when the driver provides it, and then delegates to inline `fb_fillrect()`.

## State and Persistence Behavior

No independent state is stored. It modifies framebuffer memory according to the requested rectangle, color, and raster operation.

## Dependencies and Integration Points

It integrates with drivers that use `cfb_fillrect()` fallback or default I/O-memory draw macros, and with the shared packed-pixel fill implementation in `fb_fillrect.h`.

## Risks and Edge Cases

The wrapper itself is simple; risks lie in memory-type mismatch, invalid rectangles passed by callers, low-bpp color packing, endian/byte reversal, and XOR versus copy raster operation correctness.

## Test Signals

Test copy and XOR fills for 1/2/4/8/16/24/32 bpp, unaligned rectangles, out-of-bounds clipping by upper layers, `fb_sync()` call ordering, stopped framebuffer state, and virtual-memory warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbfillrect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbimgblt.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbimgblt.c

## Purpose

This file exports `cfb_imageblit()`, the generic I/O-memory packed-pixel image blit helper used for console glyphs, logos, and software-rendered images. The complete 36-line source was read.

## Important APIs, Types, and Functions

The only runtime API is `cfb_imageblit(struct fb_info *p, const struct fb_image *image)`. It includes `cfbmem.h` for I/O-memory access and `fb_imageblit.h` for bitmap and color image conversion.

## Control Flow

The function returns if the framebuffer is not running, warns once if used on a virtual framebuffer, calls `fb_sync()` when provided, then calls inline `fb_imageblit()`.

## State and Persistence Behavior

No state is kept. It writes image pixels into framebuffer memory using the source image, pseudo-palette, and framebuffer visual/depth configuration.

## Dependencies and Integration Points

It is used by drivers and fbcon/logo paths needing a generic I/O-memory image draw helper. It depends on fbdev state, optional reverse-pixel configuration, and the shared image blit header.

## Risks and Edge Cases

Risks include low-bpp pixel-order reversal, palette index validity, 1-bit versus 8-bit image behavior, unaligned destinations, and using I/O accessors on the wrong memory type.

## Test Signals

Test 1-bit glyph images, 8-bit color logo images, truecolor pseudo-palette use, low-bpp reverse-pixel modes, unaligned x positions, stopped framebuffer state, and virtual framebuffer warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbimgblt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbmem.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbmem.h

## Purpose

This header provides I/O-memory address primitives used by the generic packed-pixel drawing templates. The complete 43-line source was read.

## Important APIs, Types, and Functions

`struct fb_address` stores an aligned base address and bit offset. `fb_address_init()` aligns `p->screen_base` down to the native word size and records the initial bit displacement. `fb_write_offset()` and `fb_read_offset()` perform word-sized `fb_writel()`/`fb_writeq()` and `fb_readl()`/`fb_readq()` accesses depending on `BITS_PER_LONG`.

## Control Flow

There is no standalone runtime flow. The drawing headers create and move `fb_address` values, then call these accessors for each modified word.

## State and Persistence Behavior

No global state exists. `fb_address` values are transient cursors over framebuffer I/O memory.

## Dependencies and Integration Points

The header depends on `struct fb_info`, `screen_base`, fbdev I/O accessors, and word-size constants. It is included before `fb_copyarea.h`, `fb_fillrect.h`, and `fb_imageblit.h` by the I/O-memory `cfb*` wrappers.

## Risks and Edge Cases

Correctness depends on `screen_base` arithmetic and alignment being valid for `__iomem` pointers and on callers using it only for I/O-memory framebuffers. 64-bit word accesses require hardware and architecture accessors to tolerate `fb_writeq()`/`fb_readq()` semantics.

## Test Signals

Validate drawing helpers on 32-bit and 64-bit builds, framebuffers with non-word-aligned `screen_base`, and architectures with strict I/O access requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/cfbmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_backlight.c

## Purpose

This file provides fbdev backlight helper functions when `CONFIG_FB_BACKLIGHT` is enabled. It builds a default brightness curve, returns the associated backlight device, and notifies backlight providers when fb blanking changes. The complete 51-line source was read.

## Important APIs, Types, and Functions

The exported functions are `fb_bl_default_curve()`, `fb_bl_device()`, and `fb_bl_notify_blank()`. They operate on `struct fb_info` fields `bl_curve`, `bl_curve_mutex`, `bl_dev`, `blank`, and `device`.

## Control Flow

`fb_bl_default_curve()` locks the curve mutex, sets index 0 to the off value, sets the first 1/16th of nonzero levels to the minimum, and fills the remaining levels linearly from min to max. `fb_bl_device()` returns `info->bl_dev`. `fb_bl_notify_blank()` compares current and previous blank states and calls either the specific backlight device notifier or the global notifier.

## State and Persistence Behavior

State is in the in-memory fbdev backlight curve and associated backlight device. There is no persistent storage.

## Dependencies and Integration Points

The file depends on the backlight subsystem and fbdev core. It is used by framebuffer drivers that coordinate display blanking with backlight power or brightness.

## Risks and Edge Cases

`fb_bl_default_curve()` assumes `max >= min`; otherwise unsigned range arithmetic wraps. Notification behavior differs depending on whether `info->bl_dev` is set, which can affect multi-backlight systems. The implementation is compiled under an `IS_ENABLED(CONFIG_FB_BACKLIGHT)` guard even though the object is conditionally built.

## Test Signals

Test default curve generation for off/min/max combinations, blank-to-unblank transitions with a bound backlight device, fallback global notifications without one, and lockdep around `bl_curve_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_chrdev.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_chrdev.c

## Purpose

This file implements the legacy `/dev/fb*` character-device file operations and registration. It routes read/write/ioctl/mmap/open/release/fsync requests to the currently registered `fb_info` instance while managing references, module ownership, console locking, compat ioctls, and deferred I/O hooks. The complete 444-line source was read.

## Important APIs, Types, and Functions

Important functions are `file_fb_info()`, `fb_read()`, `fb_write()`, `do_fb_ioctl()`, `fb_ioctl()`, `fb_compat_ioctl()`, `fb_mmap()`, `fb_open()`, `fb_release()`, optional `get_fb_unmapped_area()`, `fb_register_chrdev()`, and `fb_unregister_chrdev()`. It defines compat layouts `struct fb_fix_screeninfo32` and `struct fb_cmap32`, and file operations `fb_fops`.

## Control Flow

Open obtains the framebuffer by minor number via `get_fb_info()`, requests module autoload if missing, locks the fb, gets the fbops owner module, stores `info` in `file->private_data`, invokes driver `fb_open()`, and initializes deferred I/O mapping state when needed. Read/write validate that the file still references the currently registered fb, check operation presence and running state, then call driver methods. Ioctl handles core commands for var/fix info, var set with console mode-change checks, cmap get/set, pan, con2fb map, blank, and driver-specific fallback. Mmap serializes through `info->mm_lock` and calls driver mmap. Release flushes deferred I/O last-close behavior, calls driver release, drops module and fb references, and returns.

## State and Persistence Behavior

State includes the major-number registration, file private references to `fb_info`, fb reference counts, module refcounts, compat-translated temporary structs, and deferred I/O open counts. No persistent storage is used, but ioctls mutate framebuffer mode, cmap, pan offsets, blank state, and console mappings.

## Dependencies and Integration Points

The file depends on fbdev global registration state from `fbmem.c`, framebuffer console helpers, major number `FB_MAJOR`, module loading, console lock, compat infrastructure, deferred I/O, and driver-provided fbops. It is built when `CONFIG_FB_DEVICE=y`.

## Risks and Edge Cases

The `file_fb_info()` check prevents stale open files from operating on a newly registered fb at the same minor, but callers must still tolerate `-ENODEV` after hot-unregister. Core ioctls mix `console_lock()` and `lock_fb_info()` and are sensitive to lock ordering. Compat fix-screeninfo truncates physical addresses to 32 bits by design. `FBIO_CURSOR` is hard-disabled. Driver callbacks can still perform their own locking and error behavior under the fb lock.

## Test Signals

Test open/autoload/close paths, stale fd after unregister/re-register, read/write when stopped, all core ioctls, compat ioctls on 64-bit kernels, deferred I/O open/release/fsync, mmap serialization, module refcount failure injection, and concurrent mode set/pan/blank operations under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_chrdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_cmdline.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_cmdline.c

## Purpose

This file preserves fbdev boot-command-line option compatibility through `fb_get_options()`. It bridges legacy `video=<fbname>:<options>` parsing to the common video command-line parser. The complete 61-line source was read.

## Important APIs, Types, and Functions

The exported API is `fb_get_options(const char *name, char **option)`. It calls `__video_get_options()` from `<video/cmdline.h>` and may duplicate the returned option string with `kstrdup()`.

## Control Flow

The function treats names beginning with `offb` as Open Firmware style, asks the common parser whether the framebuffer is enabled and what option string applies, treats an option beginning with `off` as disabled, optionally returns a newly allocated option string, and returns `0` when enabled or `1` otherwise.

## State and Persistence Behavior

There is no persistent state. The caller owns any allocated option string. Boot command-line data is read through the common parser.

## Dependencies and Integration Points

It integrates fbdev drivers with the generic `video=` command-line parser. Many legacy drivers call it during probe or init to honor disable and mode options.

## Risks and Edge Cases

The return convention is historical: `0` means enabled/success and `1` means disabled, not a negative errno. The `"off"` match uses a three-character prefix, so option strings beginning with those characters disable the driver. Callers must free `*option` when non-NULL according to the comment.

## Test Signals

Test absent options, `video=name:off`, `video=name:<mode>`, `offb` names, NULL `option` storage, allocation failure behavior, and callers that expect the legacy 0/1 convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_copyarea.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_copyarea.h

## Purpose

This header implements the generic packed-pixel area-copy engine used by I/O-memory and system-memory fbdev helpers. It handles overlapping copies, bit-aligned and unaligned sources/destinations, native or foreign endian framebuffers, optional reverse pixel order within bytes, and 32/64-bit word operations. The complete 405-line source was read.

## Important APIs, Types, and Functions

Important helpers include `fb_copy_offset_masked()`, `fb_copy_offset()`, `fb_copy_aligned_fwd()`, `fb_copy_aligned_rev()`, `fb_copy_aligned()`, `fb_copy_fwd()`, `fb_copy_rev()`, `fb_copy()`, and the entry point `fb_copyarea(struct fb_info *p, const struct fb_copyarea *area)`. It relies on `struct fb_address`, `struct fb_reverse`, `fb_address_forward()`, `fb_address_backward()`, `fb_pixel_mask()`, `fb_reverse_long()`, `fb_modify_offset()`, and memory-specific `fb_read_offset()`/`fb_write_offset()`.

## Control Flow

The entry point initializes source and destination bit addresses from `screen_base`, adjusts them by source/destination coordinates and line length, chooses reverse-copy direction when destination overlaps after source in memory, and then calls `fb_copy()`. The copy engine chooses aligned fast paths when source and destination bit offsets match, otherwise it merges adjacent source words into destination words while preserving leading/trailing masked bits. Reverse copy mirrors the process from the end of each line to avoid corrupting overlapping regions.

## State and Persistence Behavior

No global state is kept. The engine mutates framebuffer memory and uses transient bit-address cursors and masks.

## Dependencies and Integration Points

The header depends on `fb_draw.h` for endian and bit helpers and on a memory accessor header such as `cfbmem.h` or `sysmem.h`. It is included into wrapper C files so the same algorithm can target I/O or system memory.

## Risks and Edge Cases

This is performance-sensitive bit arithmetic. Risks include off-by-one errors at word boundaries, incorrect reverse direction for overlapping copies, source reads at offset `-1` in unaligned paths requiring the initial aligned cursor to make that safe, low-bpp reverse-pixel combinations, and 24 bpp or other non-power-of-two bpp widths. The implementation assumes callers provide valid rectangles within framebuffer bounds or that upper layers clipped them.

## Test Signals

Use pixel-level golden tests for 1/2/4/8/15/16/24/32 bpp, x offsets crossing word boundaries, same-line and multi-line overlaps in both directions, foreign-endian framebuffers, reverse-pixel low-bpp modes, 32-bit and 64-bit builds, and randomized copy rectangles compared with a byte/bit reference model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_copyarea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_ddc.c

## Purpose

This file implements fbdev DDC/EDID reading over an I2C bit-bang adapter. It performs legacy monitor line-wake sequencing and reads one EDID block from address `0x50`. The complete 127-line source was read.

## Important APIs, Types, and Functions

The exported API is `fb_ddc_read(struct i2c_adapter *adapter)`. The internal `fb_do_probe_ddc_edid()` allocates an EDID buffer and performs the two-message I2C transaction: write offset zero, read `EDID_LENGTH` bytes.

## Control Flow

`fb_ddc_read()` drives SCL high, then makes up to three attempts. Each attempt toggles SDA/SCL with sleeps to initialize old monitors, waits for SCL high if `getscl` is available, calls the EDID probe, drives stop/cleanup sequences, and breaks on success. At exit it releases both DDC lines high to avoid powering off Apple Cinema HD displays.

## State and Persistence Behavior

No persistent state is stored. On success the caller receives a heap-allocated EDID buffer and owns freeing it. The function mutates DDC line levels during probing.

## Dependencies and Integration Points

It depends on I2C core, `i2c-algo-bit` callbacks, EDID length definitions, delays, and fbdev drivers that expose DDC GPIO/I2C adapters. It exports `fb_ddc_read()` GPL-only.

## Risks and Edge Cases

The function assumes `adapter->algo_data` is a valid `struct i2c_algo_bit_data` with required line callbacks. DDC bus timing is sleep-heavy and can fail on monitors that hold SCL low. Only one 128-byte EDID block is read; extensions require higher-level handling elsewhere. Callers must free the returned buffer.

## Test Signals

Test successful EDID read, NACK/failure cleanup, SCL-stuck retries, adapters without `getscl`, allocation failure, line-release verification, and integration with drivers parsing the returned EDID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_defio.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_defio.c

## Purpose

This file implements fbdev deferred I/O, allowing mmap writes to framebuffer memory to be collected as dirty page references and flushed to a driver callback after a delay or fsync/last-close. The complete 479-line source was read.

## Important APIs, Types, and Functions

Private state is `struct fb_deferred_io_state`, with a kref, open count, file mapping, lock, active `fb_info`, fixed pageref array, and dirty pageref list. Exported APIs include `fb_deferred_io_fsync()`, `fb_deferred_io_mmap()`, `fb_deferred_io_init()`, `fb_deferred_io_open()`, `fb_deferred_io_release()`, and `fb_deferred_io_cleanup()`. Internal flow uses `fb_deferred_io_fault()`, `fb_deferred_io_track_page()`, `fb_deferred_io_mkwrite()`, `fb_deferred_io_work()`, and pageref lookup/get/put helpers.

## Control Flow

Initialization allocates one pageref per framebuffer page, initializes delayed work, sets default delay to one second when unset, and stores state in `info->fbdefio_state`. Open records the file mapping and installs deferred I/O address-space ops. Mmap installs vm ops, marks VM flags, stores the state as `vm_private_data`, and takes module/state refs. Fault resolves a page from the driver callback, vmalloc buffer, or physical `smem_start`. Page-mkwrite records the touched page, locks it until the PTE is dirtied, schedules delayed work, and returns `VM_FAULT_LOCKED`. Workqueue processing write-protects dirty mappings under MMU, calls the driver's `deferred_io()` callback with the pageref list, and clears the list. Cleanup flushes work, detaches `info`, and drops the state ref.

## State and Persistence Behavior

State is entirely in memory: pageref array/list, delayed work, mapping pointer, open count, krefs, and framebuffer page references. Deferred writes persist only when the driver's callback copies or sends changed pages to backing hardware/storage. No file-backed persistence is implemented here.

## Dependencies and Integration Points

The file depends on mm fault/page-mkwrite APIs, rmap write-protection, page cache mapping ops, delayed work, vmalloc-to-page, optional driver `get_page()`, and the fbdev char-device open/release/fsync hooks. It is selected by `CONFIG_FB_DEFERRED_IO`.

## Risks and Edge Cases

Key risks are lifetime races between VMAs and device removal, mapping pointer replacement by multiple opens, O(n^2) sorted pageref insertion when `sort_pagereflist` is enabled, memory cost proportional to framebuffer pages, page reference handling for physical `smem_start`, and drivers failing to tolerate unsorted lists. Cleanup sets `info=NULL` under the state lock so later faults return `SIGBUS`, which is intentional but should be tested. `open_count` is protected by the fb_info lock rather than the defio mutex.

## Test Signals

Test mmap page faults, repeated writes to the same page, writes from multiple processes, delayed callback batching, fsync flushing, last-close flushing, cleanup during live VMA access, driver `get_page()` override, vmalloc and physical framebuffer backing, sorted versus unsorted pageref lists, MMU write-protection behavior, and lockdep/KASAN/KCSAN stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_defio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_draw.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_draw.h

## Purpose

This header provides common bit-address, masking, endian, palette, and reversal helpers for the generic packed-pixel framebuffer drawing engines. The complete 163-line source was read.

## Important APIs, Types, and Functions

Important APIs include `fb_address_move_long()`, `fb_address_forward()`, `fb_address_backward()`, `fb_comp()`, `fb_modify_offset()`, `fb_palette()`, `fb_right()`, `fb_left()`, `struct fb_reverse`, `fb_reverse_bits_long()`, `fb_reverse_long()`, `fb_pixel_mask()`, and `fb_reverse_init()`.

## Control Flow

Drawing engines initialize `struct fb_address`, move it by bit offsets, compute masks for leading/trailing partial words, read-modify-write masked regions, fetch pseudo-palettes for true/direct color images, and use `fb_reverse_init()` to determine whether byte or pixel bit order must be reversed for the current framebuffer.

## State and Persistence Behavior

No global state exists. The helpers operate on transient address cursors and framebuffer words.

## Dependencies and Integration Points

It depends on `struct fb_info`, endian configuration, `fb_be_math()`, optional architecture bit-reverse acceleration, `FB_REV_PIXELS_IN_BYTE`, and memory-specific read/write functions supplied by including headers. It is shared by copy, fill, and imageblit templates.

## Risks and Edge Cases

Bit-direction helpers are endian-dependent, so subtle mistakes affect every generic drawing operation. Reverse-pixel support is compiled only when enabled; drivers setting `FB_NONSTD_REV_PIX_IN_B` without the symbol will not get pixel reversal. Masking and address movement must remain valid for non-word-aligned framebuffer bases.

## Test Signals

Unit-style golden tests should cover little and big endian builds, native and foreign framebuffer endian settings, reverse-pixel low-bpp modes, masked writes at every bit offset, and address movement across word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_draw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_fillrect.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_fillrect.h

## Purpose

This header implements generic packed-pixel rectangle fill and invert operations for fbdev drawing helpers. It supports copy and XOR raster operations, arbitrary bpp up to the word size, endian conversion, low-bpp reverse pixel order, and optimized static-pattern paths for power-of-two bpp modes. The complete 279-line source was read.

## Important APIs, Types, and Functions

Important functions and types include `fb_invert_offset()`, `struct fb_pattern`, `fb_pattern_get()`, `fb_pattern_get_reverse()`, `fb_pattern_static()`, `fb_pattern_rotate()`, `pixel_to_pat()`, `bitfill()`, `bitinvert()`, `fb_fillrect_static()`, `fb_rotate()`, `fb_fillrect_rotating()`, and the entry `fb_fillrect(struct fb_info *p, const struct fb_fillrect *rect)`.

## Control Flow

The entry point converts the requested color to a repeated word pattern, initializes framebuffer address and reversal state, adjusts for rectangle x/y and line length, then chooses static or rotating pattern fill depending on bpp alignment. Copy fills overwrite masked/full words; XOR fills invert only the bits selected by the pattern. Each line advances by the framebuffer line length in bits.

## State and Persistence Behavior

There is no global state. It mutates framebuffer memory and uses temporary pattern/address state.

## Dependencies and Integration Points

The header depends on `fb_draw.h`, memory-specific read/write accessors, fbdev visual/bpp fields, `fb_be_math()`, and caller-provided `struct fb_fillrect`. It is used by `cfbfillrect.c` and system-memory equivalents.

## Risks and Edge Cases

Risks include color pattern generation for unusual bpp values such as 3, 6, 12, or 24, endian shifts on big-endian builds, XOR behavior with masks, and off-by-one errors at rectangle edges. The helper expects valid rectangle geometry; wrappers do not clip.

## Test Signals

Use randomized golden tests for copy and XOR fills across bpp values, all x bit offsets, odd widths/heights, foreign endian settings, reverse-pixel low-bpp modes, and 32/64-bit word sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_fillrect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_imageblit.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_imageblit.h

## Purpose

This header implements the generic packed-pixel image blit engine for fbdev. It converts 1-bit bitmap images and 8-bit indexed color images into framebuffer pixels, with optimized paths for common pixels-per-word layouts and support for endian and reverse-pixel behavior. The complete 495-line source was read.

## Important APIs, Types, and Functions

Important iterators are `struct fb_bitmap_iter`, `struct fb_color_iter`, and `struct fb_bitmap4x_iter`. Important helpers include `fb_bitmap_image()`, `fb_color_image()`, `fb_bitmap4x_image()`, `fb_bitblit()`, `fb_color_imageblit()`, `fb_bitmap4x_imageblit()`, `fb_bitmap1x_imageblit()`, `fb_bitmap_1ppw()`, `fb_pack()`, `fb_bitmap_2ppw()`, `fb_bitmap_4ppw()`, `fb_bitmap_imageblit()`, and entry `fb_imageblit(struct fb_info *p, const struct fb_image *image)`.

## Control Flow

The entry initializes destination bit address and reversal state, adjusts to image `dx`/`dy`, then selects color or bitmap paths based on `image->depth`. Color images read one byte per pixel and optionally translate through `info->pseudo_palette`. Bitmap images expand foreground/background colors and use optimized one/two/four-pixels-per-word paths where possible; otherwise they fall back to generic bitstream iteration. The low-level bitblitter accumulates pixels into destination words, preserves leading/trailing bits, reverses bytes/bits as required, and writes full or masked words.

## State and Persistence Behavior

No global state is kept. The helper reads source image data and writes framebuffer memory. It uses `info->pseudo_palette` transiently for true/direct color conversion.

## Dependencies and Integration Points

The header depends on `fb_draw.h`, memory-specific framebuffer accessors, `struct fb_image`, fbdev visual/depth metadata, pseudo-palette conventions, and optional `FB_REV_PIXELS_IN_BYTE`. It is included by I/O-memory and system-memory imageblit wrappers.

## Risks and Edge Cases

Risks include palette indices outside the pseudo-palette or hardware cmap range, unusual bpp values, unaligned destinations, byte order for 1/2/4 bpp modes, and source image dimensions that upper layers fail to clip. Optimized paths require careful validation against the generic bitstream path.

## Test Signals

Compare output with a reference renderer for 1-bit and 8-bit images across 1/2/4/8/16/24/32 bpp, all x offsets, truecolor pseudo-palettes, direct/pseudocolor visuals, endian variants, reverse-pixel modes, narrow images, and widths crossing word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_imageblit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_info.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_info.c

## Purpose

This file implements allocation and release of `struct fb_info` objects and optional driver-private data. The complete 80-line source was read.

## Important APIs, Types, and Functions

The exported APIs are `framebuffer_alloc(size_t size, struct device *dev)` and `framebuffer_release(struct fb_info *info)`.

## Control Flow

Allocation computes padding so private data is long-aligned after `struct fb_info`, zero-allocates the combined block, sets `info->par` when requested, stores the parent device pointer, initializes rotation hint and blank state, and initializes the backlight curve mutex when enabled. Release ignores NULL, warns and returns if the embedded refcount is nonzero, destroys the backlight mutex when enabled, and frees the allocation.

## State and Persistence Behavior

The allocated `fb_info` and private data are in-memory state only. The function initializes default blanking state to unblanked and rotation hint to -1.

## Dependencies and Integration Points

It is used by nearly all fbdev drivers before registering a framebuffer. It depends on fbdev struct layout, slab allocation, refcount discipline from registration/open paths, and optional backlight mutex state.

## Risks and Edge Cases

Drivers must call `framebuffer_release()` only after unregistering and dropping all references; otherwise the WARN path intentionally leaks rather than freeing a live object. The padding macro assumes long alignment is sufficient for private data.

## Test Signals

Test allocation with zero and nonzero private sizes, alignment of `info->par`, default field initialization, backlight mutex init/destroy under config, release with NULL, and release with artificially nonzero refcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_internal.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_internal.h

## Purpose

This internal header declares shared fbdev core state and cross-file helpers for character-device registration, logos, fbmem registration, procfs, and sysfs/device integration. The complete 84-line source was read.

## Important APIs, Types, and Functions

It declares or stubs `fb_register_chrdev()`, `fb_unregister_chrdev()`, `fb_prepare_logo()`, `fb_show_logo()`, `fb_class`, `registration_lock`, `registered_fb[]`, `num_registered_fb`, `get_fb_info()`, `put_fb_info()`, `fb_init_procfs()`, `fb_cleanup_procfs()`, `fb_device_create()`, and `fb_device_destroy()`.

## Control Flow

There is no executable flow except inline stubs. When `CONFIG_FB_DEVICE=n`, char-device/procfs functions become no-ops and `fb_device_create()`/`destroy()` manually hold and release the parent device reference that sysfs device creation would otherwise manage.

## State and Persistence Behavior

The header exposes global fbdev registration state owned by `fbmem.c`: framebuffer class, registration mutex, registered framebuffer array, and count.

## Dependencies and Integration Points

It coordinates `fb_chrdev.c`, `fb_logo.c`, `fbmem.c`, `fb_procfs.c`, and `fbsysfs.c`. External drivers should not include it; it is for core internals.

## Risks and Edge Cases

Stub behavior under `CONFIG_FB_DEVICE=n` must stay aligned with real device creation behavior, especially parent device references. Exposed globals make lock discipline important; users must hold `registration_lock` or fb references as appropriate.

## Test Signals

Build with `FB_DEVICE=y/n`, `CONFIG_LOGO=y/n`, and verify fb registration/unregistration reference balance, procfs availability, sysfs device creation, and logo stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_io_fops.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_io_fops.c

## Purpose

This file implements generic read, write, and mmap helpers for framebuffers backed by I/O memory. The complete 173-line source was read.

## Important APIs, Types, and Functions

Exported APIs are `fb_io_read()`, `fb_io_write()`, and `fb_io_mmap()`. They operate on `info->screen_base`, `info->screen_size`, `info->fix.smem_len`, `info->fix.smem_start`, `info->fix.mmio_start`, `info->fix.mmio_len`, `info->var.accel_flags`, and optional `fb_sync()`.

## Control Flow

Read validates memory type and `screen_base`, clamps offset/count to framebuffer size, allocates a page-sized bounce buffer, syncs hardware, loops copying from I/O memory into the bounce buffer and then to userspace, updates `ppos`, and returns partial progress or an error. Write mirrors the process from userspace to bounce buffer to I/O memory, returning `-EFBIG` or `-ENOSPC` when writes exceed the framebuffer. Mmap chooses framebuffer mapping or MMIO mapping based on `vm_pgoff`, rejects MMIO mapping when acceleration flags are set, sets framebuffer page protections, and calls `vm_iomap_memory()`.

## State and Persistence Behavior

No state is stored beyond updating file offsets. It reads/writes hardware framebuffer memory and may map framebuffer/MMIO regions into userspace.

## Dependencies and Integration Points

It integrates with default I/O-memory fbops macros and `/dev/fb*` file operations. It depends on fbdev I/O copy helpers, userspace copy APIs, VM page protection helpers, and driver-provided fixed screen metadata.

## Risks and Edge Cases

Large reads/writes use a bounce buffer and can return partial success on userspace copy faults. `count + p` arithmetic can overflow if not constrained by VFS-sized values. MMIO mmap exposure is blocked when `var.accel_flags` is set but otherwise depends on accurate `fix.mmio_*`. The helper warns but still operates if `FBINFO_VIRTFB` is set.

## Test Signals

Test reads/writes at EOF, beyond EOF, partial user faults, zero `screen_size` fallback to `smem_len`, `fb_sync()` ordering, MMIO mmap offsets, accel flag rejection, page protections, and warnings for virtual-memory framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_io_fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_logo.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_logo.c

## Purpose

This file prepares and displays Linux boot logos on fbdev framebuffers, including palette setup, pseudo-palette construction, mono/VGA16 expansion, rotation, centering, CPU-count repetition, and optional extra logos. The complete 508-line source was read.

## Important APIs, Types, and Functions

Global controls are `fb_center_logo` and `fb_logo_count`. Important functions include `fb_set_logocmap()`, `fb_set_logo_truepalette()`, `fb_set_logo_directpalette()`, `fb_set_logo()`, `fb_rotate_logo_*()`, `fb_rotate_logo()`, `fb_do_show_logo()`, `fb_show_logo_line()`, optional `fb_append_extra_logo()`, `fb_prepare_extra_logos()`, `fb_show_extra_logos()`, and exported core APIs `fb_prepare_logo()` and `fb_show_logo()`.

## Control Flow

`fb_prepare_logo()` skips tileblitting, module-owned fbops, and zero logo count; computes effective depth from visual/depth fields; finds the best built-in logo; determines whether cmap reset or pseudo-palette conversion is needed; accounts for rotation and centering; and returns the vertical space needed. `fb_show_logo()` chooses repeat count from `fb_logo_count` or online CPUs and calls `fb_show_logo_line()`. The show path temporarily programs cmap entries or swaps `info->pseudo_palette`, expands packed 4-bit or 1-bit logos to byte-per-pixel images when needed, optionally rotates into a temporary buffer, then calls the driver `fb_imageblit()` repeatedly.

## State and Persistence Behavior

State includes global logo selection data in `fb_logo`, extra-logo arrays when enabled, and global logo count/centering flags. It temporarily mutates the framebuffer cmap and `info->pseudo_palette` while drawing, then restores the pseudo-palette pointer. The framebuffer contents persist visually after drawing.

## Dependencies and Integration Points

It depends on built-in `linux_logo` assets, fbdev cmap APIs, `fb_find_logo()`, CPU count, framebuffer rotation constants, driver `fb_imageblit()`, and optional extra-logo config. It is invoked by fbcon/fbmem startup paths.

## Risks and Edge Cases

`fb_show_logo_line()` returns zero if the framebuffer is suspended or owned by a module, so logo visibility depends on driver ownership state. Temporary palette allocation failures silently skip drawing. Centering reduces logo count until it fits. Comments note true/direct palette limitations and ignored `msb_right`. Extra logos support only truecolor and matching logo types.

## Test Signals

Test logo preparation for mono, VGA16, CLUT224, truecolor, directcolor, pseudocolor, static pseudocolor, rotations, centered and uncentered layouts, explicit logo count, CPU-count default, allocation failure injection, extra logos, and drivers with/without `fb_imageblit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_logo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_notify.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_notify.c

## Purpose

This file implements the fbdev blocking notifier chain used to notify clients about framebuffer events. The complete 54-line source was read.

## Important APIs, Types, and Functions

The exported APIs are `fb_register_client()`, `fb_unregister_client()`, and `fb_notifier_call_chain()`. The static state is `BLOCKING_NOTIFIER_HEAD(fb_notifier_list)`.

## Control Flow

Clients register a `struct notifier_block` with the blocking notifier chain, unregister it later, and fbdev core or drivers call `fb_notifier_call_chain()` with an event value and payload pointer.

## State and Persistence Behavior

State is the in-memory notifier chain. There is no persistent storage.

## Dependencies and Integration Points

It depends on the kernel notifier API and fbdev event definitions. Backlight, console, drivers, and other display-adjacent code can subscribe or emit events through this chain.

## Risks and Edge Cases

Blocking notifier callbacks run in the caller's context and can sleep, so event callers must use appropriate context. Misbehaving callbacks can delay fbdev operations. Registration lifetime must ensure notifier blocks outlive unregister.

## Test Signals

Test register/unregister, multiple callback ordering, callback return propagation, event payload correctness, and lockdep context for callers emitting notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_procfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_procfs.c

## Purpose

This file implements `/proc/fb`, listing registered framebuffer numbers and fixed IDs when legacy fbdev device support is enabled. The complete 62-line source was read.

## Important APIs, Types, and Functions

Important functions are `fb_seq_start()`, `fb_seq_stop()`, `fb_seq_next()`, `fb_seq_show()`, `fb_init_procfs()`, and `fb_cleanup_procfs()`. Static state is `fb_proc_dir_entry`.

## Control Flow

Initialization creates a seq_file proc entry named `fb`. Seq iteration locks `registration_lock`, walks positions from 0 to `FB_MAX - 1`, and prints `<node> <fix.id>` for non-NULL `registered_fb[i]`. Cleanup removes the proc entry.

## State and Persistence Behavior

The proc entry is in-memory virtual filesystem state. Output reflects the live `registered_fb[]` array and has no persistence.

## Dependencies and Integration Points

It depends on procfs seq APIs and fbdev registration globals from `fb_internal.h`. It is part of the legacy userspace interface controlled by `CONFIG_FB_DEVICE`.

## Risks and Edge Cases

The seq iterator holds `registration_lock` across iteration, so long reads serialize framebuffer registration changes. Missing or failed proc creation returns `-ENOMEM` to core init. Output depends on drivers setting meaningful `fix.id`.

## Test Signals

Test proc creation/removal, empty output with no framebuffers, multiple registered framebuffers, concurrent register/unregister while reading, and `fix.id` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_sys_fops.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_sys_fops.c

## Purpose

This file implements generic read and write helpers for framebuffers backed by ordinary system RAM rather than I/O memory. The complete 116-line source was read.

## Important APIs, Types, and Functions

Exported APIs are `fb_sys_read()` and `fb_sys_write()`. They operate on `info->screen_buffer`, `info->screen_size`, `info->fix.smem_len`, `info->flags`, and optional `fb_sync()`.

## Control Flow

Read warns once if the framebuffer is not marked virtual, validates `screen_buffer`, clamps offset/count, syncs, copies directly from the system-memory buffer to userspace, updates `ppos`, and returns partial success or error. Write validates bounds, sets `-EFBIG` or `-ENOSPC` for oversized writes, syncs, copies from userspace into the system-memory buffer, updates `ppos`, and returns partial success or error.

## State and Persistence Behavior

No independent state is kept beyond file offsets. It mutates framebuffer system memory directly.

## Dependencies and Integration Points

It integrates with fbdev drivers using system-memory framebuffers and default sysmem fbops. It depends on userspace copy helpers and driver-provided fixed screen sizing.

## Risks and Edge Cases

Like the I/O-memory helper, arithmetic around `count + p` must avoid overflow. There is no bounce buffer, so copy faults can leave partial writes in the framebuffer. The helper warns but still operates if `FBINFO_VIRTFB` is absent.

## Test Signals

Test EOF and beyond-EOF reads/writes, partial user faults, zero `screen_size` fallback, `fb_sync()` ordering, flag warning behavior, and concurrent writes to shared system-memory buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_sys_fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcmap.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcmap.c

## Purpose

This file implements fbdev colormap allocation, copying, userspace transfer, hardware programming, default palettes, and default palette inversion. The complete 363-line source was read.

## Important APIs, Types, and Functions

Exported APIs include `fb_alloc_cmap_gfp()`, `fb_alloc_cmap()`, `fb_dealloc_cmap()`, `fb_copy_cmap()`, `fb_cmap_to_user()`, `fb_set_cmap()`, `fb_set_user_cmap()`, `fb_default_cmap()`, and `fb_invert_cmaps()`. Static default palettes include 2-, 4-, 8-, and 16-color RGB arrays and `struct fb_cmap` wrappers.

## Control Flow

Allocation frees/reallocates cmap arrays when length changes, optionally allocates transparency, resets start/len, and copies an appropriate default cmap. Copy helpers compute overlapping ranges based on source/destination starts and lengths, then copy RGB and optional transparency arrays. `fb_set_cmap()` validates the start and callbacks, either calls driver `fb_setcmap()` or iterates entries through `fb_setcolreg()`, and copies the cmap into `info->cmap` on success. `fb_set_user_cmap()` allocates a kernel cmap, copies userspace arrays in, locks the fb, applies it, unlocks, and frees temporary arrays. `fb_invert_cmaps()` bitwise-inverts all static default palette arrays.

## State and Persistence Behavior

State includes allocated cmap arrays in each `fb_info` and static default palettes marked read-mostly. Palette changes affect in-memory fb state and hardware through driver callbacks. `fb_invert_cmaps()` permanently mutates the process-wide default arrays for the running kernel.

## Dependencies and Integration Points

It depends on fbdev driver callbacks `fb_setcolreg()` and `fb_setcmap()`, userspace copy helpers, allocation APIs, and fb locking. It is used by fbdev core ioctls, drivers during initialization, fbcon, and logo palette setup.

## Risks and Edge Cases

`fb_alloc_cmap()` uses `GFP_ATOMIC`, which may fail for larger palettes under pressure; `fb_alloc_cmap_gfp()` ORs `__GFP_NOWARN` into caller flags. `fb_set_cmap()` stops iterating when `fb_setcolreg()` returns nonzero but still returns `rc` initialized to zero, so partial programming can look successful for drivers using the per-register callback. `fb_set_user_cmap()` checks integer overflow with signed `int size`, but very large lengths still need careful bounds behavior. Default cmap inversion is global and irreversible except by another inversion.

## Test Signals

Test allocation/deallocation for lengths 0/2/4/8/16/256 with and without transparency, overlapping cmap copies, userspace get/set ioctls with partial faults, driver `fb_setcmap()` versus `fb_setcolreg()` paths, per-register failure behavior, default cmap selection thresholds, and invert/uninvert cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fbcmap.c -->
