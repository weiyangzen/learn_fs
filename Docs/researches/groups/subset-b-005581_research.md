# subset-b-005581 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/stifb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/stifb.c

## Purpose
`stifb.c` is the PA-RISC framebuffer driver for HP STI/NGLE graphics devices. It binds to STI ROM-discovered devices, maps the framebuffer and NGLE register space, exposes a fixed-mode fbdev interface, programs device-specific RAMDAC/attribute/overlay state, and provides limited hardware acceleration for rectangle fill and copy.

## Important APIs, Types, and Functions
The main private state is `struct stifb_info`, which links `fb_info`, the STI ROM handle, NGLE card id, device-specific config, ROM data, and a 16-entry pseudo palette. Important setup and hardware helpers include `stifb_init_fb()`, `stifb_init_display()`, `SETUP_FB()`, `SETUP_HW()`, `SETUP_HCRX()`, `SETUP_RAMDAC()`, `CRX24_SETUP_RAMDAC()`, `ngleSetupAttrPlanes()`, `ngleResetAttrPlanes()`, `ngleClearOverlayPlanes()`, `hyperResetPlanes()`, and `hyperUndoITE()`. fbdev callbacks are `stifb_check_var()`, `stifb_setcolreg()`, `stifb_blank()`, `stifb_fillrect()`, `stifb_copyarea()`, and generic IOMEM mmap/read/write/imageblit helpers. Module entry points are `stifb_init()`, `stifb_cleanup()`, and `stifb_setup()`.

## Control Flow
`stifb_init()` parses `stifb=` options, locates the default STI ROM first, then initializes each available STI ROM through `stifb_init_fb()`. Probe validates supported NGLE ids, rejects Visualize EG double-buffer modes, chooses bpp from hardware and `bpp:` preferences, derives visible resolution from STI, maps framebuffer memory, allocates a 256-entry cmap, initializes display planes and blanking, reserves framebuffer/MMIO resources, and registers the framebuffer. Runtime mode changes are intentionally narrow: `stifb_check_var()` only accepts the current resolution and bpp. Colormap updates switch hardware into image colormap access, write the entry, and either trigger HCRX LUT load or restore normal register state. Fill/copy callbacks program NGLE bitmap-op registers and fall back to `cfb_fillrect()` for unsupported cases.

## State and Persistence
Driver state is runtime-only and stored in `fb_info`, `struct stifb_info`, resource reservations, mapped STI regions, the fbdev cmap, and the pseudo palette. Hardware-visible state includes NGLE setup registers, RAMDAC contents, overlay planes, attribute planes, framebuffer contents, HCRX Hyperbowl/LUT state, blanking bits, and selected bpp. Nothing is persisted across unload or reboot. Global init-only state includes `stifb_bpp_pref[]` and `stifb_disabled`.

## Dependencies and Integration Points
The driver depends on PA-RISC STI core discovery (`video/sticore.h`), STI ROM region descriptors, GSC register accessors, fbdev IOMEM helpers, HP-UX grfioctl compatibility headers, kernel resource reservation, and generic cfb drawing. It integrates with fb boot options, STI primary graphics ordering, and the platform firmware's current display mode rather than EDID or dynamic mode setting.

## Risks and Edge Cases
Most risk is in undocumented hardware programming sequences and fixed register constants. `SETUP_HW()` waits on device status with no timeout. Some clear-image helpers are stubs, double-buffer devices are rejected, Tomcat dual-head support is incomplete, and HCRX bpp behavior depends on ROM/device-specific config. Resource cleanup is manual and ordered; failed initialization must unwind mapped memory, cmap, and reserved regions correctly. Since mode changes are refused, userspace expecting dynamic modes will fail.

## Test Signals
Useful signals are boot tests on each supported NGLE family, `stifb=off` and `stifb=bpp:` parsing, 8-bit and HCRX 32-bit color display, palette changes, fbcon scroll exercising fill/copy acceleration, blank/unblank for each card family, mmap/read/write sanity, unload cleanup, and unsupported/double-buffer hardware rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/stifb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr1000.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr1000.c

## Purpose
`sunxvr1000.c` is a minimal Open Firmware platform fbdev driver for Sun XVR-1000 (`SUNW,gfb`) framebuffers on sparc64. It exposes the firmware-provided framebuffer as a packed-pixel fbdev device without mode setting or acceleration.

## Important APIs, Types, and Functions
`struct gfb_info` stores `fb_info`, OF node, framebuffer mapping, physical base, width, height, depth, size, and a 16-entry pseudo palette. Important functions are `gfb_get_props()`, `gfb_setcolreg()`, `gfb_set_fbinfo()`, `gfb_probe()`, and `gfb_init()`. `gfb_ops` uses default IOMEM fb operations plus `fb_setcolreg`.

## Control Flow
The device initcall checks `fb_get_options("gfb")` and registers a platform driver. `gfb_probe()` allocates `fb_info`, reads `width`, `height`, and optional `depth` from the OF node, uses resource 6 as framebuffer memory, fixes line length at 16384 bytes, maps only `line_length * height`, fills `fix` and `var`, allocates a 256-entry cmap, registers the framebuffer, and stores drvdata. `gfb_setcolreg()` only updates the truecolor pseudo palette for the first 16 entries.

## State and Persistence
State is limited to runtime fbdev structures, the framebuffer mapping, cmap, and pseudo palette. Hardware state is whatever firmware already configured; the driver does not program timings or hardware registers. There is no persistence beyond device lifetime.

## Dependencies and Integration Points
The driver depends on OF platform resources/properties, `of_ioremap()`, fbdev IOMEM helpers, and early device init. It integrates with firmware-provided display setup and fbdev clients such as fbcon.

## Risks and Edge Cases
The driver assumes resource 6 is the framebuffer and that a 16384-byte pitch is correct. Missing width/height is fatal, but unexpected depth values are mostly passed through. There is no remove callback, dynamic mode validation, hardware blanking, EDID, or acceleration. Error cleanup covers allocation and mapping but registered devices rely on system lifetime.

## Test Signals
Test on OF nodes named `SUNW,gfb`, verify resource 6 mapping, visible output at firmware mode, correct pseudo-palette colors for 24/32 bpp, behavior with missing width/height, and boot option disabling through `fb_get_options("gfb")`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr2500.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr2500.c

## Purpose
`sunxvr2500.c` is a simple PCI fbdev driver for Sun 3DLABS XVR-2500 and related boards. It maps the PCI framebuffer BAR, derives geometry from the associated OF node, and exposes the active firmware mode to fbdev.

## Important APIs, Types, and Functions
`struct s3d_info` tracks `fb_info`, `pci_dev`, OF node, framebuffer mapping/base/size, geometry, depth, and pseudo palette. Key functions are `s3d_get_props()`, `s3d_setcolreg()`, `s3d_set_fbinfo()`, `s3d_pci_register()`, and `s3d_init()`. The PCI ID table matches multiple 3DLABS device ids. `s3d_ops` uses default IOMEM operations plus colormap handling.

## Control Flow
Initialization honors `fb_modesetting_disabled("s3d")` and `fb_get_options("s3d")`, then registers the PCI driver. Probe first removes conflicting PCI aperture users, enables the device, allocates `fb_info`, locates the OF node with `pci_device_to_OF_node()`, requests BAR 1, reads `width`, `height`, and optional `depth`, computes line length from depth because OF `linebytes` is known unreliable, maps the framebuffer, initializes fbdev metadata and cmap, then registers the framebuffer.

## State and Persistence
State is per-device fbdev runtime state plus the BAR 1 mapping, cmap, and pseudo palette. The driver does not persist or restore hardware modes; it relies on existing firmware setup. It does not implement remove, blanking, panning, or mode changes.

## Dependencies and Integration Points
Dependencies include PCI, OF node association for PCI devices, aperture conflict removal, IOMEM mapping, and fbdev. It integrates with generic system firmware framebuffer handoff through `aperture_remove_conflicting_pci_devices()`.

## Risks and Edge Cases
Risk centers on assumptions about BAR 1, OF geometry, and supported depth. If depth is not 8/16/24/32, line length may remain unset. The absence of a remove callback means it is effectively system-lifetime. Truecolor pseudo-palette packing uses blue in the high byte and red at bit 8, matching this hardware path but easy to regress.

## Test Signals
Test PCI binding for listed IDs, aperture handoff, OF node absence, BAR request failure, 8/16/24/32 bpp line length, registered framebuffer geometry, palette behavior in truecolor, and boot disabling through `video=s3d:off` or modesetting disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr2500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr500.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr500.c

## Purpose
`sunxvr500.c` supports Sun 3DLABS XVR-500 Expert3D-style PCI framebuffers. It uses the RAMDAC video layout registers to locate the active 8bpp framebuffer plane, mirrors drawing into two 8bpp buffers, and programs the RAMDAC CLUT.

## Important APIs, Types, and Functions
`struct e3d_info` contains PCI/OF identity, a spinlock, framebuffer and register mappings, RAMDAC base, 8bpp buffer offsets, geometry/depth, and pseudo palette. Key functions are `e3d_get_props()`, `e3d_clut_write()`, `e3d_setcolreg()`, `e3d_imageblit()`, `e3d_fillrect()`, `e3d_copyarea()`, `e3d_set_fbinfo()`, `e3d_pci_register()`, and `e3d_init()`. `e3d_ops` wraps generic cfb drawing with mirrored writes.

## Control Flow
Probe removes conflicting apertures, requires an OF node with `device_type` to skip secondary outputs, enables PCI, reads BAR0's configured base, maps BAR1 RAMDAC registers at offset `0x8000`, reads `RAMDAC_VID_8FB_0`, `RAMDAC_VID_8FB_1`, and `RAMDAC_VID_CFG`, computes the selected framebuffer physical address and the distance between 8bpp buffers, requests BAR0, reads OF geometry, computes pitch from RAMDAC line-size log2 and depth, maps the framebuffer, allocates cmap, and registers fbdev. Drawing callbacks lock, draw once at `screen_base`, temporarily advance `screen_base` by `fb8_buf_diff`, draw again, then restore it.

## State and Persistence
Runtime state includes the RAMDAC mapping, framebuffer mapping, offset calculations, spinlock-protected CLUT and mirrored drawing, cmap, and pseudo palette. Hardware-persistent state includes RAMDAC CLUT entries and framebuffer contents until reset or reprobed. No software state persists across driver lifetime.

## Dependencies and Integration Points
The driver depends on PCI, OF properties, aperture handoff, RAMDAC register layout, cfb helpers, and fbdev IOMEM mmap/read/write. It integrates with firmware mode setup and uses `device_type` as a primary-output filter.

## Risks and Edge Cases
The two-buffer rendering is explicitly a workaround for unknown WID/attribute behavior. `screen_base` is mutated under the driver spinlock, so any path bypassing those wrappers could see only one buffer. RAMDAC register assumptions and BAR offset arithmetic are hardware-specific. Unsupported depth can leave line length invalid. There is no remove callback, blanking callback, or dynamic mode set.

## Test Signals
Signals include probe on each listed PCI ID/subsystem, secondary-output rejection, RAMDAC 8FB offset calculation, visible updates for fill/copy/image paths, CLUT writes across 0..255, truecolor pseudo-palette entries, BAR failure unwinds, and fallback when depth/pitch properties are unusual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sunxvr500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tcx.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/tcx.c

## Purpose
`tcx.c` is the SBUS/Open Firmware fbdev driver for Sun TCX framebuffers. It supports 8-bit and 24-bit TCX variants, Brooktree DAC palette programming, THC blanking, control-plane reset for 24-bit cards, legacy SBUS mmap offsets, and fbio ioctl compatibility.

## Important APIs, Types, and Functions
Important hardware structures are `struct tcx_tec`, `struct tcx_thc`, and `struct bt_regs`; private driver state is `struct tcx_par`. fbdev callbacks are `tcx_setcolreg()`, `tcx_blank()`, `tcx_pan_display()`, `tcx_sbusfb_mmap()`, and `tcx_sbusfb_ioctl()`. Setup/teardown helpers include `__tcx_set_control_plane()`, `tcx_reset()`, `tcx_init_fix()`, `tcx_unmap_regs()`, `tcx_probe()`, and `tcx_remove()`.

## Control Flow
`tcx_probe()` allocates `fb_info`, detects low-depth cards via `tcx-8-bit`, fills `var` from OF, maps TEC, THC, DAC, framebuffer RAM, and optionally the control plane, builds a per-device mmap table from OF resources, initializes DAC control registers, resets the control plane, unblanks video, allocates and installs a cmap, initializes fixed metadata, and registers fbdev. `tcx_pan_display()` is used as a reset hook. `tcx_blank()` manipulates THC video, hsync, and vsync bits. mmap/ioctl requests are delegated to SBUS helper functions with TCX-specific map and fb type data.

## State and Persistence
Per-device state stores mapped hardware blocks, the low-depth flag, blanked flag, SBUS iospace, and adjusted mmap map. Hardware state includes BT DAC registers, THC timing/blanking bits, cursor registers, control-plane contents, and framebuffer RAM. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on OF platform resources, SBUS accessors and `sbuslib.h`, `<asm/fbio.h>` legacy constants, fbdev cmap/mmap/ioctl infrastructure, and platform driver binding for `SUNW,tcx`.

## Risks and Edge Cases
`__tcx_set_control_plane()` iterates `info->fix.smem_len` u32 entries, which depends on the control-plane mapping size matching framebuffer bytes times four. Low-depth mode disables several mmap regions. The mmap resource index remapping is non-obvious. Blank powerdown does not add behavior beyond existing blank bits. Hardware cursor areas are exposed by mmap but not managed as fbdev cursor.

## Test Signals
Test 8-bit and 24-bit OF nodes, mmap offsets for RAM8BIT/RAM24BIT/control/DAC/THC, palette writes, pan-triggered reset, all blank states, fbio helper output, control-plane clearing on 24-bit cards, and remove-path unmapping/cmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tcx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tdfxfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/tdfxfb.c

## Purpose
`tdfxfb.c` is the PCI fbdev driver for 3Dfx Banshee, Voodoo3, and Voodoo5 display controllers. It programs VGA and 3Dfx video registers, exposes mode validation and panning, supports palette and truecolor pseudo-palette handling, optionally accelerates drawing, optionally provides a hardware cursor, and can create bit-banged I2C/DDC buses.

## Important APIs, Types, and Functions
The driver uses `struct tdfx_par` and `struct banshee_reg` from `include/video/tdfx.h`. Important functions include low-level VGA/MMIO helpers, `banshee_make_room()`, `banshee_wait_idle()`, `do_calc_pll()`, `do_write_regs()`, `do_lfb_size()`, `tdfxfb_check_var()`, `tdfxfb_set_par()`, `tdfxfb_setcolreg()`, `tdfxfb_blank()`, `tdfxfb_pan_display()`, optional `tdfxfb_fillrect()`, `tdfxfb_copyarea()`, `tdfxfb_imageblit()`, `tdfxfb_cursor()`, I2C/DDC setup helpers, `tdfxfb_probe()`, `tdfxfb_remove()`, and module option parsing.

## Control Flow
Probe removes conflicting apertures, enables PCI, allocates fbdev state, identifies the chip and max pixel clock, requests/maps register BAR0, calculates framebuffer size from DRAM registers, requests/maps framebuffer BAR1 with write-combining, reserves I/O BAR2 for VGA ports, optionally creates I2C/DDC buses and picks an EDID-derived mode, falls back to `640x480@60`, maximizes virtual height, allocates cmap, and registers the framebuffer. Mode set validates bpp, monitor limits, pitch, memory, pixel clock, and interlace constraints, computes PLL/timing/VGA/3Dfx register images, writes them via `do_write_regs()`, and updates `fix` metadata. Runtime drawing uses 2D engine commands when `CONFIG_FB_3DFX_ACCEL` is enabled, otherwise generic cfb helpers.

## State and Persistence
Runtime state includes MMIO base, VGA I/O base, write-combining cookie, max clock, 16-entry truecolor palette, optional I2C channel state, fbdev cmap, and hardware cursor memory carved from the end of VRAM. Hardware state includes VGA sequencer/CRTC/attribute/graphics registers, PLL, DAC, 2D engine state, cursor pattern, panning start, and palette. No disk persistence exists.

## Dependencies and Integration Points
Dependencies include PCI, aperture handoff, arch write-combining APIs, VGA register definitions, `video/tdfx.h`, fbdev mode/EDID helpers, optional `CONFIG_FB_3DFX_ACCEL`, and optional `CONFIG_FB_3DFX_I2C`. It integrates with fb boot options, module parameters `hwcursor`, `mode_option`, and `nomtrr`, and fbcon acceleration hooks.

## Risks and Edge Cases
Busy-wait loops for FIFO/idle have no timeout. Some acceleration paths assume dimensions below 4096 and contain endian-sensitive host-to-screen transfers. Cursor memory reduces `smem_len` and must remain aligned. Big-endian mode uses `MISCINIT0` byte-swapping bits. I2C GPIO operations read-modify-write shared registers. Probe error paths must undo WC, I/O regions, MMIO mappings, framebuffer mappings, and optional I2C.

## Test Signals
Test Banshee, Voodoo3, and Voodoo5 probe paths, memory-size detection, 8/16/24/32 bpp modes, pixel-clock rejection, panning and `nopan`, blank states including sync control, accelerated fill/copy/mono image blit, hardware cursor enable/disable/update, DDC EDID probing, `nomtrr`, unload cleanup, and fault injection around BAR requests and URB-like I2C failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tdfxfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tgafb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/tgafb.c

## Purpose
`tgafb.c` is the framebuffer driver for DEC 21030 TGA/SFB+ graphics devices on PCI and TurboChannel buses. It handles 8-plane, 24-plane, and 24-plus-Z variants, programs TGA timing/PLL/RAMDAC state, and implements custom accelerated image, fill, and copy operations.

## Important APIs, Types, and Functions
Private state is `struct tga_par` from `include/video/tgafb.h`, holding mapped memory, type/revision, current timing, bpp, sync-on-green, blank state, and pseudo palette. Important functions are `tgafb_check_var()`, `tgafb_set_par()`, `tgafb_set_pll()`, `tgafb_setcolreg()`, `tgafb_blank()`, `tgafb_mono_imageblit()`, `tgafb_clut_imageblit()`, `tgafb_fillrect()`, `tgafb_copyarea()`, `tgafb_init_fix()`, `tgafb_pan_display()`, `tgafb_register()`, and `tgafb_unregister()`. Bus wrappers are `tgafb_pci_register()` and `tgafb_tc_register()`.

## Control Flow
PCI probe removes conflicting apertures and calls common registration; TC probe calls the same path with TC resource handling. `tgafb_register()` enables PCI if needed, allocates `fb_info`, requests/maps the device memory resource, reads the TGA type from ROM/register space, derives framebuffer and register offsets, selects PCI or TC default modes, initializes `fix`, finds a mode, allocates cmap, calls `tgafb_set_par()`, and registers fbdev. `tgafb_set_par()` validates and stores timing, disables video, programs DEEP/rasterop/mode/base registers, computes and writes the ICS1562 PLL, initializes BT485/BT459/BT463 RAMDAC state depending on bus and depth, initializes palette/window type table, then enables video.

## State and Persistence
Runtime state lives in `fb_info` and `tga_par`: mapped device memory, framebuffer/register base pointers, card type, revision, timing registers, PLL frequency, bpp, blank flag, and palette. Hardware state includes TGA registers, PLL shift/programming bits, BT RAMDAC palettes/masks/window types, cursor-valid bits, and framebuffer contents. It does not persist across driver lifetime.

## Dependencies and Integration Points
The driver depends on PCI, optional TurboChannel, aperture handoff, `video/tgafb.h`, raw MMIO access, fbdev mode/cmap/modelist helpers, and optional VT default color tables. It integrates with `video=tgafb:mode:...`, PCI ID `DEC_TGA`, and TC IDs `PMAGD-AA`/`PMAGD`.

## Risks and Edge Cases
Several hardware waits spin until command status or retrace changes, with no timeout. Type-derived offsets index preset arrays and assume recognized hardware type. 32bpp copy falls back in general cases because pixelshift behavior is unclear. Acceleration code has many alignment, clipping, and endian assumptions. `tgafb_init()` only registers the TC driver if PCI registration returns success, so mixed build behavior deserves attention. Error cleanup must release mapped resources and cmap.

## Test Signals
Test PCI and TC binding, all TGA type variants, 8bpp-only and 32bpp-only validation, sync-on-green modes, PLL programming across common clocks, BT485/BT459/BT463 palette writes, blank/unblank and DPMS states, mono and CLUT imageblit, aligned and unaligned fill/copy, full-line scroll acceleration, pan reset behavior, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tgafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tridentfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/tridentfb.c

## Purpose
`tridentfb.c` is a PCI fbdev driver for Trident TGUI, 3DImage, Blade, BladeXP, and CyberBlade graphics chips. It programs VGA and Trident extended registers, supports flat-panel centering/stretching, DDC probing, panning, DPMS blanking, palette handling, and chip-family-specific 2D acceleration.

## Important APIs, Types, and Functions
`struct tridentfb_par` stores MMIO base, chip id, flat-panel flag, pseudo palette, acceleration function pointers, engine state, and DDC adapter data. Important helper groups include chip classifiers (`is_oldclock()`, `is_blade()`, `is_xp()`, `is3Dchip()`, `iscyber()`), DDC bit-bang callbacks, acceleration implementations for Blade, XP, Image, and TGUI families, VGA/MMIO helpers, `get_nativex()`, `set_lwidth()`, `screen_stretch()`, `screen_center()`, `set_screen_start()`, `set_vclk()`, `get_memsize()`, `tridentfb_check_var()`, `tridentfb_set_par()`, `tridentfb_setcolreg()`, `tridentfb_blank()`, `trident_pci_probe()`, and `trident_pci_remove()`.

## Control Flow
Probe removes conflicting apertures, enables PCI with devres, allocates fbdev state, refines `TGUI9660` revisions to specific chip ids, installs chip-family acceleration callbacks, requests/maps MMIO BAR1, enables MMIO, detects framebuffer size from registers or module options, requests/maps framebuffer BAR0, detects flat-panel/native width, configures fbdev flags and pixmap, creates a DDC bus and optionally selects an EDID best mode, falls back to `640x480-8@60`, allocates cmap, and registers fbdev. Mode set computes VGA timings, enables extended register access, handles panel center/stretch, writes CRTC/graphics/attribute/clock registers, configures bpp and pitch, initializes acceleration, and updates visual/cmap length.

## State and Persistence
Runtime state includes mapped MMIO/framebuffer, selected chip id, DDC adapter, pixmap buffer, pseudo palette, fbdev cmap, global module options, and selected acceleration callbacks. Hardware state includes Trident extended registers, VGA CRTC/SEQ/GFX/ATTR registers, PLL, DPMS registers, flat-panel stretch/center bits, graphics engine state, framebuffer contents, and DAC palette. No state is persisted.

## Dependencies and Integration Points
Dependencies include PCI, aperture helpers, fbdev mode/EDID/cmap APIs, `video/vga.h`, `video/trident.h`, I2C bit-banging, and cfb fallback drawing. It integrates with module/boot options for mode, bpp, acceleration, memory size adjustment, flat panel/CRT selection, native width, centering, and stretching.

## Risks and Edge Cases
Acceleration wait loops are mostly busy waits; XP has a software timeout/reset but other engines may spin. The file mutates global `tridentfb_fix`, so multi-device behavior can inherit the most recent chip's acceleration id. Some error paths do not release requested memory regions explicitly. `crt` option parsing sets `fp = 0` rather than `crt = 1`. Panel handling depends on register heuristics and user overrides. Mode validation rewrites 24 bpp to 32 bpp and adjusts virtual width for acceleration pitch constraints.

## Test Signals
Test each supported chip family, TGUI9660 revision remapping, DDC success/failure, EDID and fallback mode selection, 8/16/32 bpp validation, panning offsets, flat-panel center/stretch, memory-size overrides, noaccel fallback, accelerated fill/copy/imageblit, DPMS states, palette/pseudo-palette programming, and probe/remove resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/tridentfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/udlfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/udlfb.c

## Purpose
`udlfb.c` is a USB fbdev driver for USB 2.0-era DisplayLink devices. It maintains a virtual 16bpp system-memory framebuffer, converts dirty regions into DisplayLink bulk command streams, compresses pixel data, manages asynchronous URBs, reads or accepts EDID, exposes sysfs metrics, and keeps fbdev clients alive after USB disconnect until they close.

## Important APIs, Types, and Functions
State is `struct dlfb_data` from `include/video/udlfb.h`, containing USB device, fb_info, URB pool, backing buffer, EDID, mode limits, blank state, render/damage locks, deferred free list, metrics, and current mode. Important functions include DisplayLink command builders (`dlfb_set_register*()`, `dlfb_set_vid_cmds()`, `dlfb_set_video_mode()`), mmap/open/release/destroy callbacks, dirty rendering (`dlfb_trim_hline()`, `dlfb_compress_hline()`, `dlfb_render_hline()`, `dlfb_handle_damage()`, `dlfb_damage_work()`), deferred IO (`dlfb_dpy_deferred_io()`), EDID/mode setup (`dlfb_get_edid()`, `dlfb_setup_modes()`), sysfs handlers, vendor descriptor parsing, USB probe/disconnect, and URB pool functions (`dlfb_alloc_urb_list()`, `dlfb_get_urb()`, `dlfb_submit_urb()`, `dlfb_urb_completion()`, `dlfb_free_urb_list()`).

## Control Flow
USB probe matches DisplayLink vendor-defined interfaces, validates the bulk OUT endpoint, parses vendor descriptors for pixel limits, allocates fbdev and driver state, initializes damage work and URB pool, allocates cmap, obtains EDID or fallback modes, activates USB traffic, selects the standard channel, sets the initial mode, registers fbdev, and creates sysfs files. Updates enter through deferred IO page faults, explicit damage ioctls, fb damage callbacks, or mode-set refresh. Dirty rectangles are aligned, compared against an optional shadow buffer, encoded into RLX-style commands, split across URBs, and submitted to the bulk endpoint. Disconnect marks the device virtualized, disables USB traffic, waits for/free URBs, removes sysfs files, and unregisters fbdev; final memory release occurs in fb destroy.

## State and Persistence
Runtime state includes the virtual framebuffer, optional shadow/backing framebuffer, current mode, EDID cache, modelist, cmap, URB pool, workqueue damage rectangle, mmap/open counts, blank mode, USB active/virtualized flags, lost-pixels flag, deferred-free list, and metrics counters. Hardware state includes DisplayLink mode registers, 16bpp/8bpp base registers, blanking state, and framebuffer contents sent over USB. EDID written through sysfs is cached only in memory.

## Dependencies and Integration Points
The driver depends on USB core, fbdev deferred I/O and sysmem helpers, vmalloc/vmalloc-to-pfn mmap, EDID parsing, VESA mode database, workqueues, atomic counters, sysfs attributes, and DisplayLink-specific USB vendor/control/bulk protocols. It exposes deprecated DisplayLink ioctls for EDID and damage reporting plus sysfs `edid` and metrics files.

## Risks and Edge Cases
The render path is synchronization-heavy: framebuffer contents may change while compression reads them, mmap prevents framebuffer realloc, and URB starvation sets `lost_pixels`. `dlfb_ops_mmap()` has duplicated offset checks and maps vmalloc pages manually when defio is disabled. Damage ioctl clamps x/y but not width/height before rendering. EDID read retries byte-by-byte over control transfers and may fall back to stale/default data. Disconnect relies on virtualization so fb clients can keep using memory without USB traffic. Compression and shadow-buffer writes use unaligned 16-bit access patterns and require careful bounds.

## Test Signals
Test USB probe with valid and invalid endpoint/interface descriptors, vendor pixel-limit parsing and override, EDID read failure/fallback/sysfs write, initial mode set, mmap with and without deferred IO, explicit damage ioctl, fb damage callbacks, full-screen refresh, shadow enabled/disabled, URB allocation fallback to smaller buffers, URB timeout/submit failure/lost-pixels behavior, blank and powerdown recovery, disconnect with open clients, sysfs metrics reset, and destroy cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/udlfb.c -->
