# Research Report: subset-b-005560

This grouped report covers the requested fbdev source files under `sources/distributed-fs/ceph-client/drivers/video/fbdev/`. Each section is wrapped with the exact source path markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysimgblt.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysimgblt.c

## Purpose
`sysimgblt.c` is a small virtual-memory wrapper around the generic framebuffer image blitter. It exports `sys_imageblit()` for drivers whose framebuffer backing store is in normal CPU-addressable memory rather than I/O memory. Its main job is to select the `sysmem.h` accessors and then delegate the packed-pixel image draw to `fb_imageblit()`.

## Important APIs, Types, And Functions
The only exported API is `sys_imageblit(struct fb_info *p, const struct fb_image *image)`. The file includes `sysmem.h` before `fb_imageblit.h`, so the generic image blit template uses normal memory load/store helpers. If `CONFIG_FB_SYS_REV_PIXELS_IN_BYTE` is enabled, the wrapper defines `FB_REV_PIXELS_IN_BYTE`, altering bit order handling inside the included generic implementation.

## Control Flow And State
`sys_imageblit()` checks `FBINFO_VIRTFB`; if a driver incorrectly calls it for a non-virtual framebuffer, it emits a one-time fb warning and still calls `fb_imageblit()`. There is no persistent state in this file. All drawing effects are writes into `p->screen_buffer` through the template accessors.

## Dependencies And Integration Points
It depends on fbdev core types (`struct fb_info`, `struct fb_image`), the shared `fb_imageblit.h` implementation, and `sysmem.h` memory access helpers. It is intended to be referenced from `fb_ops.fb_imageblit` by system-memory framebuffer drivers.

## Risks And Test Signals
The main risk is misuse with I/O-memory framebuffers, where normal memory writes may be inappropriate. The warning is diagnostic only, so tests should verify that virtual framebuffer drivers set `FBINFO_VIRTFB`, render 1bpp glyph/image paths correctly, and exercise reversed-pixel-in-byte configurations when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysimgblt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysmem.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysmem.h

## Purpose
`sysmem.h` supplies normal-memory framebuffer access primitives for generic fbdev drawing templates. It abstracts a bit-addressed framebuffer base and word-level reads/writes so shared blit code can operate on CPU memory without I/O accessors.

## Important APIs, Types, And Functions
`struct fb_address` stores an aligned word address plus a bit offset into that word. `fb_address_init(struct fb_info *p)` aligns `p->screen_buffer` down to an unsigned-long boundary and computes the bit displacement from the aligned word. `fb_write_offset()` and `fb_read_offset()` write or read an `unsigned long` at a word offset relative to the stored aligned address.

## Control Flow And State
The helpers are all `static inline`; they carry no independent state and rely entirely on the caller's `struct fb_info`. The generic drawing code initializes an address once, then repeatedly reads and writes word offsets while using the bit offset to align pixel spans.

## Dependencies And Integration Points
The header depends on `struct fb_info`, `PTR_ALIGN_DOWN`, `BITS_PER_LONG`, and `BITS_PER_BYTE` from kernel headers included by the user. It is integrated by wrapper compilation units such as `sysimgblt.c` before including generic fb drawing templates.

## Risks And Test Signals
The pointer arithmetic `base - ptr.address` assumes byte-wise `void *` arithmetic as accepted by the kernel build. Incorrect use on I/O mappings would bypass required MMIO barriers/accessors. Useful test signals are unaligned `screen_buffer` bases, varied word sizes, 1bpp and packed-pixel blits crossing word boundaries, and builds with sparse/compiler warnings enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/sysmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/tileblit.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/tileblit.c

## Purpose
`tileblit.c` adapts fbcon text operations to drivers that provide tile-based acceleration through `info->tileops`. Instead of rendering font bitmaps into pixels in the fbcon core, it passes tile indices and tile geometry to hardware or driver-specific tile operations.

## Important APIs, Types, And Functions
The file defines tile versions of fbcon bitops: `tile_bmove()`, `tile_clear()`, `tile_putcs()`, `tile_clear_margins()`, `tile_cursor()`, and `tile_update_start()`. These build `fb_tilearea`, `fb_tilerect`, `fb_tileblit`, `fb_tilecursor`, and `fb_tilemap` objects. `fbcon_set_tileops()` installs `tile_fbcon_bitops` into `fbcon_par` and programs the font tilemap through `info->tileops->fb_settile()`.

## Control Flow And State
Text movement, clearing, string drawing, and cursor changes are converted from console coordinates to tile operation structs and immediately dispatched. `tile_putcs()` allocates temporary tile indices from the fb pixmap buffer via `fb_get_buffer_offset()` and masks glyph IDs with `vc_hi_font_mask` support. `tile_update_start()` pans through `fb_pan_display()` and mirrors offsets back into `par->var`. The persistent state is the selected `par->bitops` pointer and the driver's tile font map.

## Dependencies And Integration Points
This code sits between fbcon (`struct vc_data`, `struct fbcon_par`) and driver-provided `struct fb_tile_ops`. It depends on `fbcon.h`, VT/console definitions, and the fb pixmap scratch buffer. Drivers must implement all tileops used here.

## Risks And Test Signals
There is little validation around `info->tileops`; a partially initialized driver can crash. Margin clearing depends on integer division of font cell sizes and virtual resolution, so off-by-one errors are likely near non-multiple screen sizes. Tests should cover high-font-mask glyphs, right and bottom margins, panning offsets, all cursor shapes, and tile drivers with small virtual dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/core/tileblit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.c

## Purpose
`cyber2000fb.c` is the PCI fbdev driver for Integraphics CyberPro 2000, 2010, and 5000 adapters. It handles PCI aperture ownership, MMIO mapping, VGA/CyberPro register programming, accelerated fill/copy, color maps, mode validation, panning, DPMS blanking, optional DDC/I2C bit-banged buses, and suspend/resume reinitialization.

## Important APIs, Types, And Functions
`struct cfb_info` embeds `struct fb_info` and stores MMIO pointers, chip ID, reference clock, PLL divisors, palette cache, memory-control registers, RAMDAC state, pseudo palette, and optional I2C adapters. The main fb_ops are `cyber2000fb_check_var()`, `cyber2000fb_set_par()`, `cyber2000fb_setcolreg()`, `cyber2000fb_blank()`, `cyber2000fb_pan_display()`, accelerated `cyber2000fb_fillrect()` and `cyber2000fb_copyarea()`, and `cyber2000fb_sync()`. Probe/remove flows are split into `cyberpro_pci_probe()`, `cyberpro_common_probe()`, `cyberpro_pci_enable_mmio()`, `cyberpro_common_remove()`, and `cyberpro_free_fb_info()`.

## Control Flow And State
Probe removes conflicting apertures, enables PCI, allocates `cfb_info`, requests BARs, maps BAR 0, wakes the chip into linear-MMIO mode, reads memory clock registers, initializes hardware defaults, derives VRAM size from `EXT_MEM_CTL2`, selects a default mode, registers optional I2C buses, and registers the framebuffer. Mode checking normalizes bitfields for 8/16/24/32 bpp, clamps virtual dimensions to VRAM, and validates PLL/CRTC encodings. Setting mode derives pitch, fetch, pixel format, visual type, RAMDAC mode, CRTC registers, PLLs, accelerator registers, and display start. Palette entries are cached in software and written to VGA DAC registers; truecolor/directcolor update the pseudo palette. Blank/unblank changes sync control and RAMDAC powerdown bits and either zeros or restores the DAC palette. Resume replays MMIO enable, saved memory-control registers, and `set_par()`.

## Dependencies And Integration Points
The driver depends on PCI, aperture helpers, fbdev CFB drawing fallbacks, Linux I2C bit-banging, VGA-style indexed registers, and `cyber2000fb.h` register definitions. `cyber2000fb_enable_extregs()` and `cyber2000fb_disable_extregs()` are exported for companion CyberPro modules and use `func_use_count` to gate extended register access.

## Risks And Test Signals
Several paths assume `check_var()` has already rejected invalid modes; `set_par()` uses `BUG_ON()` if that contract is broken. Acceleration wait loops can time out and reset the control register. The DDC path holds `reg_b0_lock` across index-bank access, while exported extended-register access is only refcounted, so concurrent out-of-tree module access is a risk. Tests should cover PCI probe/remove error unwinds, 8/16 RGB555/RGB565/RGB444/24/32 bpp modes, ypan bounds, DPMS states, resume after mode set, DDC/I2C registration, and accelerated copy overlap directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.h

## Purpose
`cyber2000fb.h` is the private register and data contract for the CyberPro framebuffer driver and related CyberPro companion modules. It names MMIO layout, VGA extension registers, video/capture/TV/bus-master registers, graphics coprocessor registers, chip IDs, and the small external API for extended register access.

## Important APIs, Types, And Functions
The header defines `MMIO_OFFSET`, `MMIO_SIZE`, `NR_PALETTE`, RAMDAC bits, many `EXT_*` indexed register constants, capture/video format bits, bus-master offsets, TV encoder offsets, and graphics coprocessor command/mix/pixel-format registers. `struct cyberpro_info` is an outward-facing descriptor with device, I2C adapter, register/fb pointers, size, chip ID, IRQ, and opaque `struct cfb_info *info`. It declares `cyber2000fb_enable_extregs()` and `cyber2000fb_disable_extregs()`.

## Control Flow And State
The header carries no runtime control flow except optional `debug_printf()` under `DEBUG` and `CONFIG_DEBUG_LL`. Runtime state represented here is mostly hardware state exposed as named bitfields, with `struct cyberpro_info` allowing helper modules to coordinate with the main driver without seeing `struct cfb_info` internals.

## Dependencies And Integration Points
It is consumed by `cyber2000fb.c` and can be consumed by CyberPro video/capture support. It depends on kernel types such as `struct device`, `struct i2c_adapter`, and `__iomem` through including translation units. Register constants must match the hardware programming sequences in the C driver.

## Risks And Test Signals
The header contains a very broad hardware surface, much of which is not exercised by the main framebuffer path. Incorrect constants would cause silent hardware misprogramming. The optional debug function uses `vsprintf()` into a fixed buffer in debug builds. Test signals include compile coverage with DDC/I2C/capture-related users, register-bank access around `EXT_FUNC_CTL`, and runtime verification of acceleration and RAMDAC registers against known CyberPro hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/cyber2000fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/dnfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/dnfb.c

## Purpose
`dnfb.c` is a fixed-mode framebuffer driver for Apollo monochrome hardware. It exposes a 1280x1024 1bpp framebuffer and programs Apollo control registers for display enable, raster operation, and accelerated copy behavior.

## Important APIs, Types, And Functions
The driver defines Apollo register addresses through `isaIO2mem()` and many control/ROP bit macros. Its `fb_ops` provide default IOMEM read/write/mmap, `cfb_fillrect`, `cfb_imageblit`, a custom `dnfb_copyarea()`, and `dnfb_blank()`. `dnfb_probe()` allocates a `fb_info`, installs fixed var/fix structures, allocates a 2-entry cmap, registers the framebuffer, and initializes hardware registers.

## Control Flow And State
`dnfb_init()` only runs on `MACH_IS_APOLLO`, registers a platform driver, then creates a matching platform device. Probe sets `screen_base` directly from the fixed physical memory address, registers fbdev, and then resets/configures the hardware. `dnfb_blank()` toggles control register 3A. `dnfb_copyarea()` computes word-aligned masks and directional increments to use Apollo hardware copy semantics, including pre-read handling for misaligned copies.

## Dependencies And Integration Points
The file is tied to m68k Apollo/Amiga headers, platform_device infrastructure, and fbdev CFB helpers. It assumes a fixed framebuffer address and no dynamic resource discovery.

## Risks And Test Signals
There is no remove function and no resource unmap because the device is platform-fixed. `dnfb_copyarea()` has complex mask and direction math that is sensitive to x alignment, width, and overlapping regions. Tests should exercise forward and backward scroll/copy, odd x offsets, one-word and multi-word widths, blank/unblank, and boot on non-Apollo systems returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/dnfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/edid.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/edid.h

## Purpose
`edid.h` is a legacy EDID/DDC parsing helper header. It defines byte offsets and macros for extracting EDID base-block fields, especially established timings, standard timings, detailed timing descriptor fields, monitor range limits, and DPMS capability flags.

## Important APIs, Types, And Functions
The header defines constants like `EDID_LENGTH`, descriptor offsets, timing descriptor sizes, and field helpers `UPPER_NIBBLE`, `LOWER_NIBBLE`, `COMBINE_HI_8LO`, and `COMBINE_HI_4LO`. Many macros assume a local variable named `block` pointing at an EDID descriptor and expand to fields such as `PIXEL_CLOCK`, `H_ACTIVE`, `V_ACTIVE`, sync widths/offsets, sizes, flags, and range limits.

## Control Flow And State
There is no control flow or persistent state. The header is pure macro decoding. Its behavior depends entirely on the caller passing the correct 18-byte detailed timing or descriptor block as `block`.

## Dependencies And Integration Points
It is included by `fsl-diu-fb.c`, though that driver primarily uses `fb_edid_to_monspecs()` on EDID data from device tree. Other legacy fbdev code may use the macros directly for manual EDID parsing.

## Risks And Test Signals
The expression `FLAGS&3<<3` depends on C precedence and effectively masks bits after shifting `3`, which is intended but not visually obvious. Macros do not bounds-check the block pointer and may evaluate arguments multiple times. Tests should cover detailed timing descriptor extraction, monitor range descriptors, DPMS flags, malformed/short EDID data in callers, and compiler warnings for macro style.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/edid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/efifb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/efifb.c

## Purpose
`efifb.c` is the firmware framebuffer driver for EFI/UEFI systems. It binds to the `efi-framebuffer` platform device, copies firmware `screen_info`, maps the linear framebuffer with appropriate EFI memory attributes, exposes a truecolor fbdev, and optionally restores BGRT boot graphics for deferred fbcon takeover.

## Important APIs, Types, And Functions
`struct efifb_par` stores the pseudo palette plus mapped base/size. `efifb_probe()` is the central setup path. `efifb_setcolreg()` updates the 16-entry pseudo palette. `efifb_destroy()` releases the mapping, memory reservation, cmap, and framebuffer object. Option parsing is handled by `efifb_setup()` with DMI overrides and `base`, `stride`, `height`, `width`, `nowc`, and `nobgrt` options. Attribute macros expose sysfs read-only base, linelength, width, height, and depth.

## Control Flow And State
Probe validates EFI origin and framebuffer base/stride, applies options, defaults missing color fields, computes required/remapped memory size, optionally reserves the region, allocates `fb_info`, reconciles EFI memory descriptor attributes, maps with WC/UC/WT/WB, restores boot graphics if configured, initializes var/fix fields and rotation hints, allocates a 256-entry cmap, acquires the aperture, and registers the framebuffer with devm cleanup. Global state includes `use_bgrt`, `request_mem_succeeded`, and `mem_flags`.

## Dependencies And Integration Points
The driver depends on sysfb platform data, EFI memory map helpers, BGRT ACPI data, aperture arbitration, DRM panel orientation quirks, and fbdev default IOMEM ops. It is built in with `builtin_platform_driver()` so it can provide early firmware display handoff before native DRM drivers take over.

## Risks And Test Signals
`request_mem_succeeded` and `mem_flags` are global despite per-device probe structure, which is acceptable for the typical single firmware framebuffer but is a multi-device risk. Error cleanup releases `size_total` on one path while successful reservation used `size_remap`, which is worth scrutiny. BGRT BMP parsing is defensive but must avoid overruns. Tests should cover 64-bit framebuffer bases, missing stride rejection, EFI memory attributes, aperture conflicts, native DRM takeover, BGRT invalid/rotated images, and sysfs attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/efifb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ep93xx-fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/ep93xx-fb.c

## Purpose
`ep93xx-fb.c` drives the Cirrus/EP93xx integrated raster framebuffer. It allocates write-combined DMA framebuffer memory, maps LCD controller registers, programs pixel format and timing registers, manages blanking through the controller clock, and exposes fbdev operations for platform-data based boards.

## Important APIs, Types, And Functions
`struct ep93xx_fbi` stores board `ep93xxfb_mach_info`, the pixel clock, MMIO resource/base, and a 256-entry pseudo palette. Main functions include `ep93xxfb_set_pixelmode()`, `ep93xxfb_set_timing()`, `ep93xxfb_set_par()`, `ep93xxfb_check_var()`, `ep93xxfb_mmap()`, `ep93xxfb_blank()`, `ep93xxfb_setcolreg()`, `ep93xxfb_alloc_videomem()`, `ep93xxfb_probe()`, and `ep93xxfb_remove()`.

## Control Flow And State
Probe requires platform data, allocates `fb_info`, cmap, and DMA video memory, maps controller registers without claiming the resource because the backlight driver shares the block, finds a boot video mode, runs optional board setup, validates var, obtains the clock, programs the controller, enables the clock, and registers fbdev. `set_par()` sets the clock rate from pixclock, programs locked timing registers, line length, framebuffer physical address, screen lines, line step, and video attributes. `blank()` disables/enables EP93XXFB_ENABLE and the clock, with optional board blank hooks. Palette state is split between hardware LUT for pseudocolor and pseudo palette for truecolor.

## Dependencies And Integration Points
The driver depends on platform data (`linux/platform_data/video-ep93xx.h`), DMA mapping APIs, clocks, fbdev CFB helpers, and board-specific setup/teardown/blank callbacks. The mmap implementation uses `dma_mmap_wc()`.

## Risks And Test Signals
`ep93xxfb_check_var()` calls `ep93xxfb_set_pixelmode(info)` and writes hardware based on `info->var`, not the candidate `var`, so check-time side effects and stale bpp are a notable risk. The bit-27 DMA address hardware bug can reject otherwise valid allocations. Error paths use `kfree(info)` instead of `framebuffer_release(info)`, which should be checked against allocation semantics. Tests should cover all supported bpp modes, min/max resolution clamping, mmap bounds, blank clock sequencing, setup/teardown callbacks, and the bit-27 rejection parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ep93xx-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ffb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/ffb.c

## Purpose
`ffb.c` is the SPARC Creator/Creator3D/Elite3D framebuffer driver. It maps FFB/AFB FBC and DAC registers from Open Firmware platform resources, exposes SBUS-style mmap/ioctl behavior, and accelerates fill, vertical copy, and monochrome image blits through the FFB command FIFO.

## Important APIs, Types, And Functions
`struct ffb_fbc` mirrors the framebuffer controller register layout, `struct ffb_dac` wraps indexed DAC access, and `struct ffb_par` stores locks, mapped registers, flags, cached fg/bg/ROP state, physical base, fb size, board type, and pseudo palette. Key functions are `FFBFifo()`, `FFBWait()`, `ffb_switch_from_graph()`, `ffb_fillrect()`, `ffb_copyarea()`, `ffb_imageblit()`, `ffb_blank()`, `ffb_sbusfb_mmap()`, `ffb_sbusfb_ioctl()`, `ffb_probe()`, and `ffb_remove()`.

## Control Flow And State
Probe maps FBC and DAC resources, initializes state caches, fills `fb_info` from OF properties, detects AFB and DAC cursor polarity, resets the chip from graphics mode, unblanks, allocates a cmap, initializes fix fields, and registers fbdev. Drawing operations take `par->lock`, manage FIFO availability, update cached fg/bg/ROP registers only when needed, and enqueue hardware draw operations. Copyarea accelerates only vertical same-x moves and falls back to `cfb_copyarea()` otherwise. Pan display is used to force a switch out of graphics mode and rejects offsets.

## Dependencies And Integration Points
The file integrates with SPARC Open Firmware platform devices, UPA register accessors, `sbuslib` mmap/ioctl helpers, and fbdev default SBUS ops. It matches `SUNW,ffb` and `SUNW,afb` nodes.

## Risks And Test Signals
Hardware command FIFO waits can spin indefinitely until space is available in `FFBFifo()`; `FFBWait()` has a timeout and clears error bits. `ffb_imageblit()` reads four bytes per row even for narrow trailing widths, relying on the source buffer being padded enough. Tests should cover OF probe/remove, AFB vs FFB DAC cursor handling, blank/unblank, accelerated fill/copy/image paths, fallback paths, mmap offsets in `ffb_mmap_map`, and console switching from graphics mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/ffb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/fm2fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/fm2fb.c

## Purpose
`fm2fb.c` supports BSC FrameMaster II and Helfrich Rainbow II Zorro framebuffer cards for Amiga systems. These are simple 32bpp truecolor framebuffers with fixed PAL/NTSC modes and a tiny control register for interlace, enable, complement, and ROM selection.

## Important APIs, Types, And Functions
The driver defines fixed `fb_fix_screeninfo`, two `fb_var_screeninfo` modes, `fm2fb_blank()`, `fm2fb_setcolreg()`, `fm2fb_probe()`, option parsing through `fm2fb_setup()`, and Zorro driver registration in `fm2fb_init()`. It uses `FB_DEFAULT_IOMEM_OPS`.

## Control Flow And State
Probe requests the Zorro device, allocates `fb_info` with pseudo palette storage, allocates a 256-entry cmap, maps the 2MB card aperture, stores the control register pointer, fills the framebuffer with EBU color bars, unblanks the display, selects PAL by default unless options requested NTSC, and registers fbdev. Global state is limited to `fm2fb_reg` and selected `fm2fb_mode`.

## Dependencies And Integration Points
It depends on the Zorro bus, Amiga I/O mapping, and fbdev core. The hardware has no programmable timing beyond board jumpers/control bits, so the mode database is fixed.

## Risks And Test Signals
The color-bar initialization writes through a pointer derived from the physical start address rather than the mapped `screen_base`, which is a notable portability and correctness risk. There is no remove path. `fm2fb_blank()` always sets non-interlaced when unblanking. Tests should cover Zorro probe failure/unwind, PAL/NTSC option parsing, blank/unblank control register values, pseudo palette updates for regno < 16, and framebuffer mapping behavior on the target architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/fm2fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/fsl-diu-fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/fsl-diu-fb.c

## Purpose
`fsl-diu-fb.c` is the Freescale Display Interface Unit fbdev driver. It exposes five framebuffer devices representing one base plane and four additional AOIs, manages DIU descriptors, modes, gamma/cursor memory, open-count based panel enablement, IRQ workarounds, monitor-port selection, and platform-specific DIU operations.

## Important APIs, Types, And Functions
`struct fsl_diu_data` is the coherent DMA state block containing five `fb_info` objects, AOI metadata, DIU register pointer, descriptors, gamma table, cursor buffers, dummy AOI, EDID data, IRQ, and monitor port. `struct mfb_info` tracks each AOI's index, id, open count, descriptor, alpha, display offsets, and parent. Key functions include `fsl_diu_check_var()`, `fsl_diu_set_par()`, `fsl_diu_pan_display()`, `fsl_diu_ioctl()`, `fsl_diu_open()`, `fsl_diu_release()`, `fsl_diu_cursor()`, `install_fb()`, `fsl_diu_probe()`, `fsl_diu_remove()`, `fsl_diu_isr()`, suspend/resume hooks, and monitor sysfs handlers.

## Control Flow And State
Initialization validates platform `diu_ops.set_pixel_clock`, handles module/boot options, optionally allocates cache-coherency scratch memory, and registers the OF platform driver. Probe allocates aligned coherent `fsl_diu_data`, initializes descriptors and AOI metadata, reads EDID from device tree, maps DIU registers, obtains IRQ, initializes dummy descriptors, disables stale interrupts, requests IRQ, installs all five fbdevs, and creates a `monitor` sysfs file. Opening an fb increments its AOI count; the first open validates mode, allocates framebuffer memory if needed, programs descriptors, enables interrupts, and links the AOI into the DIU descriptor chain. Release unlinks the AOI and disables interrupts only when all AOIs are closed. Plane 0 mode changes reprogram gamma, timing, pixel clock, display size, and LCDC mode.

## Dependencies And Integration Points
The driver depends on OF address/IRQ APIs, PowerPC/Freescale `diu_ops`, `linux/fsl-diu-fb.h` ioctl/descriptor definitions, fbdev EDID helpers, DMA coherent memory, big-endian MMIO accessors, and optional MPC512x gamma ioctls. It integrates user controls through fb ioctls for pixel format, AOI display offset, alpha, chroma key, and gamma plus sysfs monitor selection.

## Risks And Test Signals
The driver has complex shared state across five fbdevs under a global spinlock; descriptor-chain ordering for paired AOIs is a major correctness area. `map_video_memory()` uses `virt_to_phys()` on pages from `alloc_pages_exact()`, which relies on DMA-suitable low memory. `fsl_diu_cursor()` does 32-bit reads from potentially short cursor image buffers by design. Probe error handling uninstalls all fbdevs after partial install. Tests should cover EDID preferred-mode fallback, all bpp modes, AOI overlap/position clamping, open/release counts, every ioctl path including bad user pointers and chroma bounds, IRQ underrun reset, suspend/resume with open AOIs, monitor sysfs changes, and non-coherent cache builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/fsl-diu-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/g364fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/g364fb.c

## Purpose
`g364fb.c` is a fixed hardware framebuffer driver for MIPS Magnum/Jazz G364 8-plane graphics. It exposes the ARC-initialized display as an 8bpp pseudocolor fbdev and supports palette programming, vertical panning, and blanking.

## Important APIs, Types, And Functions
The file defines fixed G364 register addresses, control bits, a static `fb_info`, initdata fix/var defaults, `g364fb_pan_display()`, `g364fb_blank()`, `g364fb_setcolreg()`, and `g364fb_init()`. `fb_ops` use default IOMEM ops plus those custom methods.

## Control Flow And State
Init reads the current resolution from hardware display registers after temporarily disabling the timing generator, sets a simple hardware cursor pattern, computes line length and VRAM size from the Jazz R4030 config register, fills `fb_info`, allocates a 255-entry cmap, and registers the framebuffer. Panning rejects x offsets and out-of-range y offsets, then writes `TOP_REG`. Blanking toggles `FORCE_BLANK` in `CTLA_REG`. Palette writes go to every other entry at `CLR_PAL_REG`.

## Dependencies And Integration Points
The driver is tied to MIPS Jazz physical/virtual register mappings, ARC firmware-initialized display timings, and fbdev core. There is no dynamic platform device or remove path.

## Risks And Test Signals
Direct casts to fixed physical/virtual addresses assume the target memory map. Cmap allocation length is 255 despite accepting regno 255, which should be scrutinized. `fb_var.yres_virtual = smem_len / xres` omits bytes-per-pixel explicitly but is correct for 8bpp only. Tests should cover Jazz-only boot, palette entry 255, pan bounds, blank/unblank register state, and behavior when framebuffer registration fails after cmap allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/g364fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/gbefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/gbefb.c

## Purpose
`gbefb.c` drives the SGI GBE framebuffer, especially SGI O2/IP32 graphics. It allocates or maps framebuffer memory, programs GBE timing/PLL/DMA registers, hides the hardware's tiled scanout behind a linear CPU view, supports CRT and 1600SW flat panel defaults, and exposes fbdev operations plus sysfs memory size/revision attributes.

## Important APIs, Types, And Functions
`struct gbefb_par` stores the active var, computed timing, WC cookie, and validity flag. Global state includes mapped `gbe` registers, framebuffer memory and DMA/physical addresses, tile table, revision, ypan/ywrap flags, pseudo palette, hardware cmap cache, and monitor mode selection. Main functions include `gbe_turn_off()`, `gbe_turn_on()`, `gbe_loadcmap()`, `compute_gbe_timing()`, `gbe_set_timing_info()`, `gbefb_set_par()`, `gbefb_check_var()`, `gbefb_setcolreg()`, `gbefb_mmap()`, `gbefb_probe()`, and `gbefb_remove()`.

## Control Flow And State
Probe registers through a platform driver and, on SGI IP32, creates a platform device. It requests the MMIO region, maps GBE registers, allocates a coherent tile table, maps boot-reserved memory or allocates write-combined framebuffer memory, installs a WC mapping cookie, fills the tile table with 64KB tile physical blocks, allocates cmap, resets GBE, finds a requested/default mode, validates it, encodes fix fields, and registers fbdev. Mode set computes PLL/timing, turns GBE off, programs timing registers, initializes WID mode registers, sets frame tile/table DMA registers to make hardware scan memory linearly, initializes gamma/cmap, and turns GBE on. mmap remaps each 64KB tile separately to userspace.

## Dependencies And Integration Points
The driver depends on `video/gbe.h` register field macros, DMA allocation APIs, MIPS cache attributes, platform devices, and fbdev CFB drawing helpers. The `mem:` and `monitor:` boot options influence allocation size and default timing.

## Risks And Test Signals
The linearization trick requires `xres * yres * bpp` to meet a divisibility constraint; `gbefb_check_var()` rejects unsupported cases. Power sequencing uses polling loops with timeout diagnostics but no hard failure propagation. Global state limits multiple-device support. mmap must correctly split across tile boundaries and set architecture-specific cache attributes. Tests should cover 8/16/32 bpp modes, rejected 800x600x8-style divisibility failures, tile-boundary mmap ranges, CRT vs 1600SW mode setup, cmap FIFO timeouts, blank/unblank sequencing, and probe error unwind for framebuffer allocation and MMIO reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/gbefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Kconfig

## Purpose
`geode/Kconfig` defines the configuration menu for AMD Geode framebuffer support. It gates family-level framebuffer support and enables separate LX, GX, and GX1 framebuffer drivers.

## Important APIs, Types, And Functions
The file defines `FB_GEODE` as a bool depending on `FB`, `PCI`, x86 or compile-test support, and not UML. It defines tristate `FB_GEODE_LX`, `FB_GEODE_GX`, and `FB_GEODE_GX1`, each depending on `FB_GEODE`, selecting `FB_IOMEM_HELPERS`, and documenting the module names `lxfb`, `gxfb`, and `gx1fb`.

## Control Flow And State
Kconfig has no runtime state. Its selections determine which Geode driver objects are compiled and whether they are built-in or modules.

## Dependencies And Integration Points
It integrates with the kernel configuration system, fbdev, PCI, architecture constraints, and the Makefile in the same directory. The `FB_IOMEM_HELPERS` selection aligns these drivers with framebuffer I/O memory helper ops.

## Risks And Test Signals
Misconfigured dependencies could expose Geode drivers on unsupported architectures or omit required helpers. Test signals are Kconfig compile coverage for x86_32, x86 compile-test, module and built-in combinations, and confirming UML excludes the family menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Makefile

## Purpose
`geode/Makefile` maps Geode framebuffer Kconfig symbols to the object groups that implement each driver.

## Important APIs, Types, And Functions
It builds `gx1fb.o` for `CONFIG_FB_GEODE_GX1`, `gxfb.o` for `CONFIG_FB_GEODE_GX`, and `lxfb.o` for `CONFIG_FB_GEODE_LX`. Composite object lists are `gx1fb_core.o display_gx1.o video_cs5530.o`, `gxfb_core.o display_gx.o video_gx.o suspend_gx.o`, and `lxfb_core.o lxfb_ops.o`.

## Control Flow And State
There is no runtime behavior. Build state is derived directly from Kconfig symbols.

## Dependencies And Integration Points
The Makefile integrates the display-controller files researched here with core and video-output files in the Geode directory. Object composition shows that display programming is split from chip-specific core probing and video output configuration.

## Risks And Test Signals
Missing object dependencies would produce unresolved symbols such as `gx1_dc_ops` or GX display helpers. Test signals are allmodconfig/allyesconfig builds and individual module builds for `gx1fb`, `gxfb`, and `lxfb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx.c

## Purpose
`display_gx.c` programs the AMD Geode GX display controller for the `gxfb` driver. It calculates framebuffer size and line pitch, disables/reprograms the display controller for a requested fb mode, sets timings and pixel format, delegates dot-clock/display-output details, and writes hardware palette entries.

## Important APIs, Types, And Functions
`gx_frame_buffer_size()` determines VRAM size either from GLIU MSR ranges when VSA2 is absent or from VSA virtual registers when present. `gx_line_delta()` returns an 8-byte aligned pitch. `gx_set_mode()` is the main display programming function. `gx_set_hw_palette_reg()` writes RGB888 palette entries through DC palette registers.

## Control Flow And State
`gx_set_mode()` unlocks DC registers, disables the timing generator, waits for pending memory requests, disables FIFO/compression, sets DCLK through `gx_set_dclk_frequency()`, clears unused config bits, configures FIFO priority, framebuffer offset, pitch, line size, graphics/video enable bits, pixel format for 8/16/32 bpp, horizontal and vertical active/blank/sync timings, writes display/general config, calls `gx_configure_display()`, and relocks the controller.

## Dependencies And Integration Points
It depends on `gxfb.h` for register accessors and DC bit definitions, CS5535/VSA helpers, MSR reads, and video-output functions implemented in the GX driver objects. It is included in the `gxfb` composite module.

## Risks And Test Signals
The mode path assumes validated timing fields and only handles 8/16/32 bpp. FIFO priority is fixed with comments noting possible tuning for high resolutions. Framebuffer size discovery diverges sharply based on VSA2 presence. Tests should cover VSA and non-VSA systems, pitch alignment, all supported bpp formats, high-resolution FIFO stability, palette writes, and lock/unlock register sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.c

## Purpose
`display_gx1.c` implements display-controller operations for the AMD Geode GX1 framebuffer. It discovers GX base/framebuffer memory size, programs GX1 display timings and output config, delegates video clock/output work, and writes the GX1 6-bit-per-channel hardware palette.

## Important APIs, Types, And Functions
`gx1_read_conf_reg()` safely maps GX1 configuration registers through I/O ports 0x22/0x23 under `gx1_conf_reg_lock`. `gx1_gx_base()` derives the GX base address from `CONFIG_GCR`. `gx1_frame_buffer_size()` maps memory-controller registers, computes total DIMM size, reads graphics base, and returns memory above that base. `gx1_set_mode()` and `gx1_set_hw_palette_reg()` are installed in exported `gx1_dc_ops`.

## Control Flow And State
Mode set unlocks DC registers, blanks and disables timing, waits, disables FIFO/compression, clears DCLK bits, calls `vid_ops->set_dclk()`, sets DCLK divider, waits for clock settle, constructs general/output/timing config, sets framebuffer offset, line delta, buffer size, panel output bits, horizontal and vertical timings, writes final configs, calls `vid_ops->configure_display()`, and relocks. State is mostly MMIO register state in `geodefb_par`; global state is only the config-register spinlock.

## Dependencies And Integration Points
It depends on `geodefb.h`, `display_gx1.h`, port I/O, MMIO, and the companion GX1 video ops (`video_cs5530.o`). It is part of the `gx1fb` composite module.

## Risks And Test Signals
The DIMM loop checks the low half after shifting `bank_cfg`; this compact code deserves hardware validation. `gx1_set_mode()` comments flag possible DCLK divider and pixel/line doubling gaps. Tests should cover config register locking under concurrent access, framebuffer-size detection with different DIMM layouts, 8bpp vs non-8bpp output config, palette quantization, clock-settle timing, and panel output configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.h

## Purpose
`display_gx1.h` is the GX1 display-controller register definition header. It declares GX1 display helper APIs and names configuration, memory-controller, palette, timing, output, cursor, and buffer register offsets and bitfields.

## Important APIs, Types, And Functions
It declares `gx1_gx_base()`, `gx1_frame_buffer_size()`, and `extern const struct geode_dc_ops gx1_dc_ops`. Constants include `CONFIG_CCR3`, `CONFIG_GCR`, memory controller `MC_BANK_CFG` and `MC_GBASE_ADD`, DC unlock/general/timing/output config bitfields, framebuffer/cursor/video offsets, line delta, buffer size, horizontal/vertical timing registers, and palette registers.

## Control Flow And State
The header carries no runtime control flow. It encodes the register contract consumed by `display_gx1.c` and GX1 core code.

## Dependencies And Integration Points
It depends on `struct geode_dc_ops` from `geodefb.h` being visible to users. The constants must remain synchronized with GX1 hardware programming in `display_gx1.c`.

## Risks And Test Signals
Duplicate definitions of `DC_PAL_ADDRESS` and `DC_PAL_DATA` appear in the header, harmless but noisy. Incorrect masks or shifts would silently corrupt timing/output programming. Test signals are build coverage, register write audits against GX1 documentation, and runtime mode tests for all fields programmed by `gx1_set_mode()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/display_gx1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/geodefb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/geodefb.h

## Purpose
`geodefb.h` defines the common private interface between Geode framebuffer core drivers, display-controller backends, and video-output backends. It allows GX/GX1/LX-style code to share operation tables without merging chip-specific register programming.

## Important APIs, Types, And Functions
`struct geode_dc_ops` provides `set_mode()` and `set_palette_reg()` hooks. `struct geode_vid_ops` provides `set_dclk()`, `configure_display()`, and `blank_display()` hooks. `struct geodefb_par` stores CRT enable state, optional flat-panel dimensions, display and video MMIO bases, and pointers to the selected DC/video ops.

## Control Flow And State
There is no runtime logic in the header. The persistent state represented by `geodefb_par` is attached to `fb_info->par` and consumed by display and video modules during mode set, palette update, and blanking.

## Dependencies And Integration Points
It depends on fbdev types through including translation units. `display_gx1.c` includes it directly; GX code uses a sibling `gxfb.h` but follows the same split between display and video operations.

## Risks And Test Signals
The abstraction is intentionally thin, so callers must ensure ops pointers and MMIO bases are initialized before use. Tests should cover probe initialization of `geodefb_par`, null/unsupported panel dimensions, blanking through `vid_ops`, and palette/mode callbacks for each Geode variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/geodefb.h -->
