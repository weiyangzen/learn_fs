# Research Group subset-b-005553

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/Kconfig

## Purpose
This Kconfig file is the build-time feature matrix for legacy Linux fbdev drivers. It defines the top-level `FB` menuconfig, common helper symbols, hardware-specific framebuffer drivers, optional per-driver subfeatures, and subordinate Kconfig includes for fbdev subdirectories. For this work item it gates the Acorn VIDC, Amiga native chipset, Arc monochrome LCD, ARK 2000PV, and Asiliant/Chips 69000 drivers that are built by the local Makefile.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. Its key "APIs" are symbols and dependency expressions consumed by Kbuild, users, and defconfigs. `menuconfig FB` is a tristate root that selects `FB_CORE` and `FB_NOTIFY`; all driver symbols depend on it directly or indirectly. Common helper symbols include `FB_HECUBA`, `FB_SVGALIB`, `FB_MACMODES`, and `FB_SBUS_HELPERS`, each selected by drivers that need shared code.

The relevant local symbols are `FB_ACORN`, `FB_AMIGA`, `FB_AMIGA_OCS`, `FB_AMIGA_ECS`, `FB_AMIGA_AGA`, `FB_ARC`, `FB_ARK`, and `FB_ASILIANT`. They express platform constraints, helper selection, and module eligibility: `FB_ACORN` is bool-only for built-in Acorn ARM platforms, `FB_AMIGA` is tristate and has per-chipset bools, `FB_ARC` is tristate with `HAS_IOPORT` and x86/compile-test gating, `FB_ARK` is tristate and depends on PCI plus `HAS_IOPORT`, and `FB_ASILIANT` is bool-only for built-in PCI systems.

## Control Flow
Kconfig evaluation starts at `menuconfig FB`; if disabled, the rest of the fbdev driver tree is unavailable. Enabling `FB` exposes architecture/platform driver choices and subordinate options. Helper symbols are selected by drivers, so selecting `FB_ARC` automatically pulls in deferred sysmem helpers and selecting `FB_ARK` pulls in the cfb drawing helpers, I/O memory fb file operations, and SVGALIB helper layer. At the end of the file, subdirectory Kconfigs for `geode`, `omap`, `omap2`, `mmp`, and `core` are sourced so the menu extends beyond the flat file.

The Amiga flow is a notable hierarchy: `FB_AMIGA` enables the driver, while `FB_AMIGA_OCS`, `FB_AMIGA_ECS`, and `FB_AMIGA_AGA` choose supported chip generations. The C driver has compile-time fallbacks if none are set, but normal configuration should choose at least one relevant generation.

## State and Persistence
Kconfig state persists in kernel configuration outputs such as `.config`, generated `include/config/*` files, and built module lists. The file itself keeps no runtime state. Its choices persist into compile-time `CONFIG_*` macros that conditionally include driver code, constants, and hardware paths.

## Dependencies and Integration Points
The file integrates with Kbuild through symbol names consumed in `drivers/video/fbdev/Makefile`. It also integrates with architecture capabilities such as `ARM`, `ARCH_ACORN`, `AMIGA`, `PCI`, `HAS_IOPORT`, `COMPILE_TEST`, and helper subsystems including `APERTURE_HELPERS`, `FB_IOMEM_HELPERS`, `FB_SYSMEM_HELPERS_DEFERRED`, `FB_CFB_FILLRECT`, `FB_CFB_COPYAREA`, `FB_CFB_IMAGEBLIT`, `FB_MODE_HELPERS`, `VIDEOMODE_HELPERS`, and bus-specific libraries.

## Risks and Edge Cases
Several drivers are legacy and architecture-specific, so incorrect dependency relaxation can allow builds that compile but are unusable or unsafe on unsupported hardware. Bool-only symbols such as `FB_ACORN` and `FB_ASILIANT` prevent module builds; changing them would require code lifetime and remove-path review. Helper selections are part of the ABI between Kconfig and C code: dropping `FB_IOMEM_FOPS`, cfb helpers, or deferred sysmem helpers would lead to unresolved operations or missing fbops. `COMPILE_TEST` increases build coverage but can hide runtime assumptions about real I/O ports, VGA primary devices, or platform-provided memory.

## Test Signals
Useful validation includes `olddefconfig` and `allmodconfig`/`allyesconfig` builds for supported architectures, compile-test builds for `FB_ARC` and PCI VGA drivers, and checking that each selected symbol produces the expected object in the Makefile. For this group, direct signals are `CONFIG_FB_ACORN=y` building `acornfb.o`, `CONFIG_FB_AMIGA=m/y` building `amifb.o c2p_planar.o`, `CONFIG_FB_ARC=m/y` building `arcfb.o`, `CONFIG_FB_ARK=m/y` building `arkfb.o`, and `CONFIG_FB_ASILIANT=y` building `asiliantfb.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/Makefile

## Purpose
This Makefile maps fbdev `CONFIG_*` symbols to object files and subdirectories. It is the Kbuild companion to the Kconfig menu, ensuring that selected legacy framebuffer drivers and helper libraries are compiled into built-in objects or modules.

## Important APIs, Types, and Functions
The main interface is Kbuild's `obj-y` and `obj-$(CONFIG_...)` syntax. `obj-y += core/` always descends into the fbdev core directory. Relevant mappings for this work item are `obj-$(CONFIG_FB_ACORN) += acornfb.o`, `obj-$(CONFIG_FB_AMIGA) += amifb.o c2p_planar.o`, `obj-$(CONFIG_FB_ARC) += arcfb.o`, `obj-$(CONFIG_FB_ARK) += arkfb.o`, and `obj-$(CONFIG_FB_ASILIANT) += asiliantfb.o`. The file also adds helper objects such as `macmodes.o`, `sbuslib.o`, and `wmt_ge_rops.o` when their symbols are enabled.

## Control Flow
Kbuild evaluates the Makefile after configuration. Built-in `y` objects are linked into the kernel or parent built-in archive; module `m` objects are compiled into modules where the symbol permits modules. Hardware-specific drivers are listed first, platform and fallback drivers later, and the virtual test framebuffer is last. Subdirectories such as `matrox/`, `aty/`, `sis/`, `via/`, `geode/`, `mmp/`, `omap/`, `omap2/`, and `mb862xx/` are entered based on fixed or conditional object assignments.

## State and Persistence
The Makefile holds no runtime state. Its persistent effect is build output: generated `.o`, `.ko`, built-in archives, and dependency files. The `CONFIG_FB_AMIGA` mapping persists an important linkage relation by always adding `c2p_planar.o` with `amifb.o`, because `amifb.c` calls `c2p_planar()` for multi-bit image blits.

## Dependencies and Integration Points
This file integrates directly with `Kconfig` symbols and with the source files in the same directory. It is also an integration point for shared helper subdirectories and vendor subtrees. Driver code assumes the correct helper selections from Kconfig; the Makefile assumes those helpers and source files are present under the same kernel tree.

## Risks and Edge Cases
Misaligning the Makefile with Kconfig breaks builds either by omitting required companion objects or by compiling code when dependencies are not met. The Amiga driver is a concrete example: dropping `c2p_planar.o` would break `amifb_imageblit()` for non-1bpp image expansion. Shared subdirectory entries such as unconditional `obj-y += omap/ omap2/` rely on each subdirectory's own Kconfig/Makefile logic to avoid unwanted objects. Duplicated helper object inclusion, such as `macmodes.o` on multiple Apple/ATI lines, is intentional Kbuild behavior but should be reviewed if moving helpers.

## Test Signals
Check `make drivers/video/fbdev/` or targeted builds with the relevant configs set. Inspect generated module names: `amifb`, `arcfb`, `arkfb` where tristate allows modules, and built-in object presence for bool-only `acornfb` and `asiliantfb`. Link-time success with `CONFIG_FB_AMIGA` verifies the `c2p_planar.o` companion. `make W=1` can catch stale object references after source renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.c

## Purpose
`acornfb.c` is a platform framebuffer driver for Acorn ARM video hardware, primarily VIDC20 on Risc PC style systems. It registers one fbdev instance, allocates or uses display memory, validates monitor/video timings, programs VIDC/IOMD or MEMC display registers, manages the VIDC palette, and supports vertical panning/ywrap.

## Important APIs, Types, and Functions
Global driver state is split between static `struct fb_info fb_info`, `struct acornfb_par current_par`, and `struct vidc_timing current_vidc`. `current_par` records monitor type, DRAM/VRAM choice, palette cache, pseudo-palette, screen end address, and DPMS flag. The fb operation table uses `FB_DEFAULT_IOMEM_OPS`, `acornfb_check_var`, `acornfb_set_par`, `acornfb_setcolreg`, and `acornfb_pan_display`.

VIDC20 timing and palette programming are handled by `acornfb_set_timing()` and `acornfb_setcolreg()`. Timing validation and normalization are done by `acornfb_adjust_timing()`, `acornfb_validate_timing()`, and `acornfb_check_var()`. Boot/module options are parsed by `acornfb_setup()` with handlers for `mon:`, `montype:`, and `dram:`. Initialization runs through `acornfb_init_fbinfo()` and `acornfb_probe()`.

## Control Flow
`module_init()` registers a platform driver named `acornfb`. Probe reads `fb_get_options("acornfb")`, initializes the static fb_info once, resolves monitor specs from explicit options or default monitor detection, chooses a default mode from `modedb` that matches monitor ranges, and selects VRAM or allocated write-combining DRAM. It then calls `fb_find_mode()` with the local mode database and fallback paths, prints selected monitor/display settings, applies the variable mode with `fb_set_var()`, and registers the framebuffer.

Mode setting flows from fbdev into `acornfb_check_var()` then `acornfb_set_par()`. `check_var` validates bpp, pixel clock, adjusted memory geometry, and monitor sync ranges. `set_par` chooses palette size and visual type, computes line length, programs DMA start/end/control registers, updates the display DMA address, and writes VIDC timings. Panning only updates the hardware start address after checking ywrap/ypan bounds.

## State and Persistence
State is process-wide and effectively singleton. Palette values are cached in `current_par.palette`; current timing is cached in `current_vidc` to avoid rewriting unchanged VIDC timing registers. Framebuffer memory is either physical VRAM advertised by setup code through `vram_size` or DMA-allocated write-combining DRAM. Hardware state persists in VIDC/IOMD/MEMC registers until mode change or reset; there is no disk persistence.

## Dependencies and Integration Points
The driver depends on Acorn architecture headers, `mach/acornfb.h` helpers such as `acornfb_default_control()`, `acornfb_default_econtrol()`, `acornfb_valid_pixrate()`, and `acornfb_vidc20_find_rates()`, plus hardware accessors `vidc_writel()`, `iomd_writel()`, and `memc_write()` depending on platform defines. It integrates with the platform bus, fbdev core, fb mode helpers, DMA allocation, and `/dev/fb*`.

## Risks and Edge Cases
The driver uses static global state and has no remove path, matching old built-in platform assumptions but limiting hotplug/lifetime robustness. Probe leaks allocated DRAM if later `fb_find_mode()` or `register_framebuffer()` fails on VIDC20 paths. Monitor detection currently assumes SVGA, so unsafe monitor timings are possible if the user does not supply correct `mon:` or `montype:` options. `acornfb_parse_montype()` allows `montype == NR_MONTYPES`, which later falls back to SVGA because probe checks `> NR_MONTYPES`; this off-by-one-style boundary deserves care. The 16bpp VIDC20 palette path rewrites all 256 hardware palette entries on each logical palette update and must be tested for flicker/performance.

## Test Signals
Validation should cover boot with no options, explicit `montype:vga`, `montype:svga,dpms`, custom `mon:hmin-hmax:vmin-vmax`, `dram:` overrides, VRAM and DRAM framebuffer paths, all supported bpp modes, and ywrap/ypan bounds. Hardware signals include correct VIDC timing writes, `IOMD_VID*` or MEMC DMA register updates, palette changes in pseudocolor and directcolor modes, and successful fb console operation at the selected default mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.h

## Purpose
`acornfb.h` provides private data structures and VIDC20 register constants for the Acorn framebuffer driver. It defines palette encodings, mode/timing helper records, per-device state, and bitfields used when composing VIDC20 control, external control, and data control register writes.

## Important APIs, Types, and Functions
`struct vidc20_palette`, `struct vidc_palette`, and `union palette` model VIDC20 and older VIDC palette encodings. `struct acornfb_par` is the driver's private state container, holding the device pointer, framebuffer end address, DRAM/VRAM metadata, palette size, monitor type, VRAM/DPMS flags, a 256-entry palette cache, and a 16-entry pseudo-palette. `struct vidc_timing` carries computed horizontal/vertical VIDC register values, control bits, and VIDC20 PLL control. `struct modey_params` and `struct modex_params` describe mode tables used by Acorn-specific timing helpers.

The macro set defines `VIDC_PALETTE_SIZE`, `VIDC_NAME`, `EXTEND8`, `EXTEND4`, and many VIDC20 constants such as `VIDC20_CTRL_*`, `VIDC20_ECTL_*`, and `VIDC20_DCTL_*`.

## Control Flow
The header has no executable control flow. It is included by `acornfb.c`; if `HAS_VIDC20` is defined it pulls in `asm/hardware/iomd.h` and exposes VIDC20-specific constants. The C file fills `struct vidc_timing`, writes fields using the register bit masks, and stores palette entries in the union representation before issuing `vidc_writel()` calls.

## State and Persistence
The header defines layouts for runtime state but does not allocate state itself. Persistent runtime values are stored by `acornfb.c` in `current_par` and `current_vidc`. Register bit definitions persist into compiled code as constants.

## Dependencies and Integration Points
The header depends on Acorn platform compile-time symbols, especially `HAS_VIDC20`, and on type definitions from Linux/architecture headers included before or by the including C file. It is tightly coupled to VIDC/VIDC20 hardware programming and to helper code that computes VIDC20 PLL and default control values.

## Risks and Edge Cases
The palette structs use C bitfields, which are sensitive to compiler and endianness assumptions; this is acceptable only because the code targets the matching Acorn architecture/hardware representation. `struct acornfb_par` statically sizes its palette array to `VIDC_PALETTE_SIZE`, so non-VIDC20 builds must still provide a coherent palette size definition path. Register constants should be updated only with hardware documentation because wrong bit assignments can disable output, change bus width, or alter sync polarity.

## Test Signals
Header-level validation is indirect: compile VIDC20 and non-VIDC20 configurations, confirm register constants generate the expected writes in `acornfb_set_timing()`, and test palette programming for mono, pseudocolor, 16bpp directcolor, and 32bpp directcolor modes on real hardware or a hardware-aware emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/amifb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/amifb.c

## Purpose
`amifb.c` is the framebuffer driver for Amiga native OCS, ECS, and AGA chipsets. It translates fbdev modes into Amiga custom-chip display registers, manages planar framebuffer memory in Chip RAM, builds Copper lists for display updates and ywrap, handles palette and blanking, implements a hardware sprite cursor API, and provides custom planar drawing routines.

## Important APIs, Types, and Functions
The central private type is `struct amifb_par`, which stores decoded mode geometry, pixel clock tag, line scaling, display window coordinates, DMA fetch registers, bitplane pointers/modulos, chipset-specific register values, and cursor geometry. Global state includes chipset capability tables (`pixclock`, `maxdepth`, `maxfmode`, `chipset`), memory pointers (`videomemory`, `spritememory`, `dummysprite`), Copper list storage in `copdisplay`, vblank latches (`do_vmode_full`, `do_vmode_pan`, `do_blank`, `do_cursor`), blank/cursor state, and saved color zero.

Mode conversion is handled by `ami_decode_var()`, `ami_encode_var()`, `ami_update_par()`, `ami_build_copper()`, `ami_rebuild_copper()`, `ami_init_display()`, and `ami_update_display()`. fbdev entry points are `amifb_check_var`, `amifb_set_par`, `amifb_setcolreg`, `amifb_blank`, `amifb_pan_display`, `amifb_fillrect`, `amifb_copyarea`, `amifb_imageblit`, and `amifb_ioctl`. Custom ioctls expose `FBIOGET_FCURSORINFO`, `FBIOGET_VCURSORINFO`, `FBIOPUT_VCURSORINFO`, `FBIOGET_CURSORSTATE`, and `FBIOPUT_CURSORSTATE`.

## Control Flow
The platform driver probes `amiga-video`. Probe parses boot options, disables DMA, allocates `fb_info`, classifies the hardware as OCS/ECS/AGA, sets maximum depth/fetch mode/video memory size, derives pixel clock values from `amiga_eclock`, patches the mode database, chooses monitor specs, finds a startup mode, and allocates one Chip RAM block for framebuffer, sprite memory, dummy sprite, and Copper lists. It maps video memory write-through when possible, initializes a safe Copper list, enables display/Copper/blitter/sprite DMA, requests `IRQ_AMIGA_COPPER`, allocates a colormap, and registers the framebuffer.

Mode setting calls `ami_decode_var()` to validate and round fbdev timing, bpp, scrolling, DMA fetch limits, ywrap, and memory layout. `amifb_set_par()` then rebuilds Copper lists and sets `do_vmode_full`, so the actual hardware switch happens in `amifb_interrupt()` at Copper/vblank time. Panning similarly updates decoded offsets, recomputes bitplane pointers, and sets `do_vmode_pan`. The interrupt applies pending display changes, initializes full modes, rebuilds Copper pointer sequences, updates or flashes the hardware cursor, and processes blank/unblank requests.

Drawing is software-driven and planar-aware. For 1bpp images it expands bits into each plane with unaligned bit-copy helpers; for deeper images it calls `c2p_planar()`. Fill and copy paths operate directly on planar memory using bit-level functions that support unaligned packed operations and overlapping copies.

## State and Persistence
All state is volatile and hardware-resident. Chip RAM holds framebuffer pixels, sprite data, and Copper programs. `struct amifb_par` plus global latches describe the current and pending display state. Palette writes update Amiga color registers immediately except color zero while blanked. Hardware state persists until mode change, blanking, driver removal, or system reset; the driver does not persist settings to disk.

## Dependencies and Integration Points
The driver depends on Amiga architecture interfaces: `amiga_custom`, `amiga_chip_alloc/free`, `amiga_chip_avail`, `ZTWO_PADDR`, `ZTWO_VADDR`, `amiga_eclock`, `amiga_vblank`, `amiga_chipset`, `AMIGAHW_PRESENT`, `IRQ_AMIGA_COPPER`, and `amifb_video_off()`. It integrates with fbdev core, platform devices, user-copy ioctls, Chip RAM allocation, Amiga DMA/Copper registers, and `c2p_planar.o` from the Makefile.

## Risks and Edge Cases
This driver is highly timing-sensitive. Incorrect `min_fstrt`, monitor capabilities, or mode timing can steal DMA cycles from audio, floppy, refresh, or sprites. The vblank latch variables are global and not protected by a general lock; they depend on fbdev call serialization and interrupt-time ordering. Some cursor user-copy paths contain comments noting unchecked `get_user`/`put_user` return values, so fault handling is incomplete. `amifb_blank()` records a pending blank but returns before hardware has applied it. The driver has many chipset-specific compile-time paths; OCS only supports broadcast modes, ECS/AGA add programmable sync, and AGA adds higher depths/fetch modes. Custom bit-copy routines are performance-critical but risk subtle boundary errors with unaligned 32/64-bit accesses.

## Test Signals
Validation should include OCS, ECS, and AGA boot probes; PAL/NTSC and VGA mode selection; `monitorcap:`, `fstart:`, `inverse`, and `ilbm` boot options; mode switches across bpp and interlace/doublescan modes; ywrap and ypan scrolling; blank, hsync suspend, vsync suspend, and powerdown; palette updates including AGA high/low color writes; cursor ioctl get/set/state/flash behavior; planar fill/copy/imageblit clipping and overlap; and interrupt-driven application of pending mode and pan changes. Hardware tests should watch for audio/floppy disruption from aggressive fetch starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/amifb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/arcfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/arcfb.c

## Purpose
`arcfb.c` drives the Arc monochrome LCD board, a KS108-controller panel array accessed through host I/O ports used as data/control GPIO. It exposes a virtual 1bpp framebuffer in system memory and flushes dirty regions to the physical LCD by translating linear framebuffer bytes into KS108 64x8 page writes.

## Important APIs, Types, and Functions
`struct arcfb_par` stores the data/control/secondary-control I/O port addresses, an atomic open reference count, a chip-select lookup table, `fb_info`, optional IRQ, and a spinlock. Module parameters define the hardware contract: `num_cols`, `num_rows`, `dio_addr`, `cio_addr`, `c2io_addr`, `splashval`, `tuhold`, `nosplash`, `arcfb_enable`, and `irq`.

Low-level KS108 accessors are `ks108_writeb_ctl()`, `ks108_writeb_mainctl()`, `ks108_readb_ctl2()`, `ks108_writeb_data()`, `ks108_set_start_line()`, `ks108_set_yaddr()`, `ks108_set_xaddr()`, and `ks108_clear_lcd()`. Framebuffer flushing is split through `arcfb_lcd_update()`, `arcfb_lcd_update_horiz()`, `arcfb_lcd_update_vert()`, and `arcfb_lcd_update_page()`. Deferred sysmem fbops are generated by `FB_GEN_DEFAULT_DEFERRED_SYSMEM_OPS()`, with `arcfb_damage_range()` and `arcfb_damage_area()` as damage hooks.

## Control Flow
The module only starts if `arcfb_enable` is set. Init registers a platform driver and creates a matching platform device. Probe computes video memory size from `64*64*num_cols*num_rows/8`, allocates a zeroed vmalloc backing store, allocates `fb_info`, validates required I/O port parameters, optionally requests an IRQ, registers the framebuffer, initializes each LCD chip, and optionally splashes/clears all chips.

Writes to the framebuffer go through deferred sysmem operations. Damage callbacks compute affected pixel rectangles, align them to KS108 page/chip boundaries, and issue page writes. Each page update reads 8 vertical pixels from the flat framebuffer and packs them into the controller's vertical-byte format. `fb_pan_display` supports ywrap within a 64-line chip by changing KS108 display start line registers. `FBIO_WAITEVENT` waits on an optional interrupt and then falls through to `FBIO_GETCONTROL2`, returning the secondary control byte.

## State and Persistence
The driver maintains a vmalloc shadow framebuffer and pushes changes to the LCD. LCD contents and controller registers persist in hardware until overwritten or reset. Module parameters are static for the module lifetime. The interrupt wait queue is global. There is no disk persistence.

## Dependencies and Integration Points
The file depends on x86-style I/O port access (`inb/outb`), platform devices, fbdev deferred sysmem helpers, vmalloc, delays, wait queues, interrupts, and `linux/arcfb.h` ioctl definitions. It integrates with users through `/dev/fb*`, fbdev drawing/mmap/write paths mediated by deferred I/O, module parameters, and optional hardware IRQ signaling.

## Risks and Edge Cases
The driver does not request or reserve the I/O port ranges before using `outb/inb`, so conflicts with other drivers or firmware reservations are possible. `cslut` is statically sized and only initializes entries 0 and 1, even though comments describe larger panel arrays; `num_cols * num_rows` greater than the lookup coverage risks invalid chip selects. Missing or zero `tuhold` can violate KS108 hold timing. `FBIO_WAITEVENT` schedules after `prepare_to_wait()` without an explicit condition loop, so signals/spurious wakeups and missed events need scrutiny. Probe cleanup always calls `free_irq(par->irq, info)` after register failure, even when no IRQ was requested, relying on `par->irq` being zero. The backing store size and default `var` are not adjusted from `num_cols/num_rows`, so non-128x64 configurations need careful testing.

## Test Signals
Tests should cover disabled module load, missing I/O addresses, 2x1 128x64 panel writes, larger `num_cols/num_rows` configurations, deferred write/mmap damage flushing, ywrap panning under 64 lines, splash and no-splash modes, `FBIO_GETCONTROL2`, `FBIO_WAITEVENT` with and without IRQ, and timing sensitivity for different `tuhold` values. Hardware validation should compare pixel locations against expected KS108 page/chip mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/arcfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/arkfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/arkfb.c

## Purpose
`arkfb.c` is a PCI framebuffer driver for ARK 2000PV VGA hardware with an ICS5342 RAMDAC. It maps the linear framebuffer, programs VGA/SVGA timing and ARK extended registers, controls the RAMDAC pixel mode and PLL, implements fbdev mode setting, and provides optimized 4bpp image/fill paths.

## Important APIs, Types, and Functions
`struct arkfb_info` stores memory clock metadata, write-combining cookie, RAMDAC object, saved VGA state, open mutex/refcount, and pseudo-palette. Supported fb formats are described by `arkfb_formats`; timing register mappings are described by `ark_timing_regs` and associated `vga_regset` arrays.

The RAMDAC abstraction uses `struct dac_ops` and `struct dac_info`, with ICS5342 implementation in `ics5342_set_mode()`, `ics5342_set_freq()`, `ics5342_release()`, and `ics5342_init()`. Driver fbops include `arkfb_open`, `arkfb_release`, `arkfb_check_var`, `arkfb_set_par`, `arkfb_setcolreg`, `arkfb_blank`, `arkfb_pan_display`, `arkfb_fillrect`, `arkfb_imageblit`, and cfb copyarea helpers. PCI lifecycle is handled by `ark_pci_probe`, `ark_pci_remove`, `ark_pci_suspend`, and `ark_pci_resume`.

## Control Flow
Module init rejects operation if modesetting is disabled, accepts a boot/module `mode_option`, and registers a PCI driver for device `0xEDD8:0xA099`. Probe removes conflicting aperture users, ignores secondary VGA devices, allocates `fb_info`, enables the PCI device, requests regions, initializes the ICS5342 DAC, maps BAR0 write-combining, derives a VGA I/O base, detects memory size from sequencer register 0x10, finds the startup mode, allocates a 256-entry colormap, registers the framebuffer, stores driver data, and adds write-combining via `arch_phys_wc_add()`.

Open saves VGA mode/fonts/cmap on the first open; release restores VGA state and resets the DAC when the last opener exits. Mode setting unlocks CRT registers, blanks the display, resets VGA register groups, enables ARK linear framebuffer/full memory access, programs the FIFO threshold and offset, selects a mode-specific sequencer/CRT/DAC path, computes and writes the pixel clock, programs SVGA timings, clears visible memory, and unblanks the device.

## State and Persistence
Runtime state resides in `struct arkfb_info` plus hardware registers. The saved VGA state persists only while the framebuffer is open and is restored on last release. The framebuffer memory mapping and write-combining cookie persist until remove. Module parameters `mode_option` and `threshold` influence default mode and FIFO threshold for the module lifetime.

## Dependencies and Integration Points
The driver depends on PCI, fbdev core, aperture conflict removal, VGA/SVGA helper APIs from `linux/svga.h` and `video/vga.h`, cfb drawing helpers, console locking for suspend/resume, architecture write-combining helpers, and VGA primary-device detection. It integrates with users through fbdev, with system firmware/console state through VGA save/restore, and with PCI resource management.

## Risks and Edge Cases
The code deliberately ignores secondary VGA devices because it has no VGA arbitration support. Memory size is read from an ARK sequencer register with a FIXME; wrong firmware state could produce an incorrect size. Several optimized 4bpp paths assume 8-pixel alignment and fall back only when the wrapper detects unsupported cases. `pci_disable_device()` is commented out in error/remove paths, which is a legacy choice but can leave enable state to PCI core/system policy. Suspend/resume only reprograms hardware when `ref_count` is nonzero, so closed framebuffers may resume without a refreshed mode until reopened. RAMDAC mode/frequency failures in `arkfb_set_par()` may leave previous clocking active while other registers change.

## Test Signals
Validation should include probe on primary and secondary VGA placements, aperture conflict removal with VGA/DRM firmware drivers, default and user-specified modes, text mode, 4bpp packed/interleaved, 8/16/24/32bpp modes, DAC PLL boundary frequencies, palette programming, blank/unblank/powerdown, ypan, first-open save and last-close restore, suspend/resume with open and closed fb, and FIFO threshold variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/arkfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/asiliantfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/asiliantfb.c

## Purpose
`asiliantfb.c` is a compact PCI framebuffer driver for Asiliant/Chips 69000-family display controllers, especially the 69030/69000 class. It maps the controller framebuffer/MMIO aperture, initializes indexed VGA and flat-panel registers, computes dot-clock PLL settings, supports 8/16/24bpp fbdev modes, and registers a legacy fbdev device.

## Important APIs, Types, and Functions
The driver uses `struct fb_info` directly, with a 16-entry pseudo-palette allocated as framebuffer private memory. Indexed register helpers `mm_write_xr`, `mm_write_fr`, `mm_write_cr`, `mm_write_gr`, `mm_write_sr`, and `mm_write_ar` write Asiliant/VGA register banks through MMIO offsets under `mmio_base = screen_base + 0x400000`.

Mode and color entry points are `asiliantfb_check_var()`, `asiliantfb_set_par()`, and `asiliantfb_setcolreg()`. `asiliant_calc_dclk2()` computes PLL divisor and m/n fields from `pixclock` using `Fref = 14318180`. `asiliant_set_timing()` programs CRT timing, line width, panel/CRT selector, and misc output. Static register tables `chips_init_sr/gr/ar/cr/fr/xr` are applied by `chips_hw_init()`. PCI lifecycle is `asiliantfb_pci_init()` and `asiliantfb_remove()`.

## Control Flow
Module init checks `fb_modesetting_disabled("asiliantfb")`, honors `fb_get_options("asiliantfb", NULL)`, and registers a PCI driver for `PCI_VENDOR_ID_CT` and `PCI_DEVICE_ID_CT_69000`. Probe removes conflicting aperture users, validates BAR0 memory, reserves the memory region, allocates `fb_info`, maps 8 MiB of the aperture, writes PCI command/config bits directly, performs a small MMIO output write, initializes fb defaults, allocates a 256-entry colormap, registers the framebuffer, initializes hardware register tables, and stores driver data.

When fbdev requests a mode, `check_var` validates dot clock limits and normalizes virtual resolution to the visible resolution. It supports 8bpp pseudocolor, 16bpp RGB555/RGB565 based on red offset, and 24bpp RGB888. `set_par` computes DCLK2 PLL values, programs pixel pipeline mode, line length, visual type, clock registers, and timing registers. Palette writes program hardware DAC entries and update the pseudo-palette for the first 16 truecolor entries.

## State and Persistence
The driver keeps minimal software state: fb_info, colormap, pseudo-palette, and the MMIO mapping. Hardware register state persists in the display controller until reset or driver reprogramming. It has no suspend/resume path and no disk persistence.

## Dependencies and Integration Points
Dependencies include PCI, fbdev IOMEM operations, aperture conflict removal, MMIO accessors, memory resource reservation, and legacy VGA-style indexed register behavior. User-space integration is the fbdev node; hardware integration is PCI BAR0 where both framebuffer and MMIO register windows are mapped.

## Risks and Edge Cases
Probe maps a fixed 8 MiB window while `fix.smem_len` is 2 MiB and the resource size is only validated for being nonzero; small or differently laid-out BARs could be overmapped. `pci_enable_device()` is not called, and the driver writes PCI config dword 4 directly instead of using PCI helpers, which is fragile across platforms. There is no power-management handling. `check_var` does not reject unsupported bpp values explicitly after handling 8/16/24, so an unsupported bpp may reach `set_par()` with incomplete color fields. Dot-clock calculation has no failure return if no valid m/n pair is found; best values start as `0xffffffff`, so invalid arithmetic would be dangerous if constraints are wrong. The code registers the framebuffer before `chips_hw_init()`, so users could theoretically observe an fb before hardware programming completes.

## Test Signals
Validation should include PCI probe/remove, BAR/resource-size sanity, aperture handoff from firmware fb, 640x480 default mode, 8bpp palette writes, RGB555 and RGB565 16bpp pseudo-palette, 24bpp truecolor, dot-clock limits below 3.125 MHz and above 220 MHz, mode timing changes between LCD/CRT selector paths, and failure cleanup for region reservation, ioremap, colormap allocation, and framebuffer registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/asiliantfb.c -->
