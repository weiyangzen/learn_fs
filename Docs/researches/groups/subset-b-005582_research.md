# subset-b-005582 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/uvesafb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/uvesafb.c

## Purpose
`uvesafb.c` is a framebuffer driver for VBE 2.0+ graphics adapters that can execute real-mode VBE BIOS services through the userspace `v86d` helper. Unlike `vesafb`, it discovers VBE modes at runtime, can read EDID/DDC data, can set VBE modes after boot, exposes VBE metadata through sysfs, and optionally uses the protected-mode interface on 32-bit x86 for palette and panning operations.

## Important APIs, Types, And Functions
The driver registers a platform driver/device named `uvesafb` and exposes `fb_ops` entries for open/release, colormap handling, panning, blanking, `fb_check_var`, and `fb_set_par`. The connector path is built around `struct uvesafb_ktask`, `struct uvesafb_task`, `uvesafb_exec()`, `uvesafb_cn_callback()`, and the global `uvfb_tasks[]` table protected by `uvfb_lock`. VBE discovery and mode work is handled by `uvesafb_vbe_getinfo()`, `uvesafb_vbe_getmodes()`, `uvesafb_vbe_getedid()`, `uvesafb_vbe_getmonspecs()`, `uvesafb_vbe_init_mode()`, and `uvesafb_set_par()`. Sysfs attributes expose VBE version, modes, OEM strings, `nocrtc`, and the driver-level `v86d` helper path.

## Control Flow
Module initialization parses boot/module options, installs the connector callback, registers the platform driver, creates the synthetic platform device, and adds the `v86d` driver attribute. Probe allocates `fb_info`, performs VBE info/mode/EDID/state-size discovery through `v86d`, chooses an initial mode, allocates a cmap, reserves VGA I/O and framebuffer memory, maps the LFB write-combining, registers the fbdev, and creates device attributes. A mode change validates a requested resolution/depth against cached VBE mode info, optionally builds a VBE 3.0 CRTC block, asks the helper to invoke function `0x4f02`, and falls back to BIOS-default timings if custom timings fail.

## State And Persistence
Persistent state is kernel-resident: module parameters, `v86d_path`, cached VBE blocks/mode arrays in `struct uvesafb_par`, monitor specs, selected mode index, MTRR/write-combine cookie, original VBE state buffers, and a refcount that controls save/restore around first open and last release. The driver also persists user-visible state through registered framebuffer state and sysfs attributes. It does not write disk state.

## Dependencies And Integration Points
It depends on Linux fbdev, connector/netlink, platform devices, `call_usermodehelper()`, `v86d`, VBE structures from `<video/uvesafb.h>`, EDID helpers, VGA I/O on x86, memory resource management, and architecture write-combine helpers. It integrates with fbcon/userspace through `/dev/fb*`, sysfs, and module/boot options such as `scroll`, `mtrr`, `nocrtc`, `noedid`, `vbemode`, and `v86d`.

## Risks
The helper protocol is security-sensitive: replies require `CAP_SYS_ADMIN` and ack/sequence validation, but correctness depends on trusted `v86d` behavior and bounded connector payloads. Hardware mode switches can fail or leave display state inconsistent; fallback to default timings helps but does not cover every BIOS quirk. PMI code is limited to non-NX 32-bit x86. Global `uvesafb_ops` is mutated to disable blanking/panning, which is safe for a single synthetic device but would be fragile for multiple instances. Memory sizing, VBE string offsets, and mode tables depend on BIOS-reported data.

## Test Signals
Useful signals are successful `uvesafb` probe logs, a registered framebuffer, populated `/sys/.../vbe_*` attributes, working `fbset` mode changes, palette tests in 8 bpp, panning tests when PMI is enabled, blank/unblank behavior, module unload cleanup, and negative tests where `v86d` is missing, EDID is unavailable, custom CRTC timings fail, or memory reservation/ioremap fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/uvesafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.c

## Purpose
`valkyriefb.c` implements the fbdev driver for Apple's Valkyrie display controller on supported PowerMac and 68k Macintosh systems. It maps the framebuffer, colormap registers, and Valkyrie control registers, chooses a Mac video mode/color mode from boot options, NVRAM, or monitor sense, then exposes a packed-pixel framebuffer.

## Important APIs, Types, And Functions
Key local state is split between `struct fb_par_valkyrie` for selected vmode/cmode geometry and `struct fb_info_valkyrie` for embedded `fb_info`, mapped register pointers, physical addresses, monitor sense, VRAM size, and pseudo palette. `valkyriefb_ops` provides `fb_check_var`, `fb_set_par`, `fb_setcolreg`, and `fb_blank`. Core helpers include `valkyrie_choose_mode()`, `read_valkyrie_sense()`, `valkyrie_var_to_par()`, `valkyrie_par_to_fix()`, `valkyrie_init_info()`, and `set_valkyrie_clock()`.

## Control Flow
Initialization parses `video=valkyriefb:` options, rejects unsupported machines, locates physical addresses either from hardcoded 68k Macintosh addresses or Open Firmware node resources, allocates driver state, reserves/maps memory, chooses the initial mode, initializes `fb_info`, programs hardware through `valkyriefb_set_par()`, and registers the framebuffer. Mode validation converts fbdev `var` into Mac vmode/cmode through `mac_var_to_vmode()`, verifies table support, rejects virtual panning/offsets, and checks VRAM. Setting a mode resets the controller, writes mode/depth registers, sets clock parameters over CUDA IIC when available, delays, then re-enables output.

## State And Persistence
State is held in the singleton allocated `fb_info_valkyrie`. Boot-selected defaults are static globals and may be seeded from NVRAM. The hardware state is programmed directly into memory-mapped registers; colormap writes are sent to the cmap register pair. There is no runtime remove path in this file, so initialization-time cleanup only covers failures before registration.

## Dependencies And Integration Points
The driver depends on fbdev, Mac monitor-mode helpers in `macmodes.h`, register tables in `valkyriefb.h`, NVRAM and Open Firmware support on PowerMac, ADB/CUDA for clock programming when configured, and machine detection on 68k Mac. It integrates with fbcon through the generic framebuffer registration and with boot options `vmode:` and `cmode:`.

## Risks
The hardware support is highly platform-specific. Address discovery differs between CONFIG_MAC and Open Firmware systems, and the 68k path uses fixed physical addresses. Mode support is table-driven and rejects panning/virtual resolutions. `set_valkyrie_clock()` is compiled out without CUDA, which may leave clock programming dependent on firmware defaults. Because the driver uses a module init path rather than a modern platform driver remove path, teardown coverage is limited.

## Test Signals
Signals include correct machine filtering, successful resource mapping, monitor sense logs, selected mode/cmode logs, registered `valkyrie` framebuffer, correct CLUT updates in 8 bpp, pseudo-palette behavior in 16 bpp, blank/powerdown register effects, and failure tests for unsupported modes, insufficient VRAM, missing OF resources, or failed ioremaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.h

## Purpose
`valkyriefb.h` contains the register layout and mode initialization tables used by `valkyriefb.c`. It translates the sparse, padded Valkyrie MMIO layout into C structures and maps supported Mac `VMODE_*` entries to mode register values, pixel-clock programming bytes, pitch values, and visible resolution.

## Important APIs, Types, And Data
`VALKYRIE_REG_PADSIZE` encodes the different register spacing used by m68k Mac versus other platforms. `struct cmap_regs` describes the color-map address/data pair. `struct vpreg` models a padded one-byte register, and `struct valkyrie_regs` groups mode, depth, status, interrupt, and monitor-sense registers. `struct valkyrie_regvals` records one mode's control byte, three clock parameters, color-mode indexed pitches, and resolution. `valkyrie_reg_init[]` indexes supported modes by `VMODE_MAX` position.

## Control Flow
The header has no executable control flow, but `valkyriefb.c` uses the table as the central decision point for mode validation and programming. The selected `valkyrie_regvals` drives VRAM size calculation, `fix.line_length`, mode/depth writes, and clock programming. Unsupported modes have `NULL` entries, and unsupported 16 bpp modes use a zero pitch entry.

## State And Persistence
The table is static kernel data. It persists for the lifetime of the module/kernel and is treated as immutable mode capability data. It does not allocate resources or store runtime state.

## Dependencies And Integration Points
The header expects Mac mode constants from `macmodes.h` via the including source. It is tightly coupled to `valkyriefb.c` and the underlying Valkyrie register map. Some 1024x768 modes are only compiled for non-CONFIG_MAC builds.

## Risks
Mode accuracy depends on hard-coded historical timing and clock parameter values. Incorrect pitch or clock bytes can produce an unusable display. The table shape assumes `CMODE_8` and `CMODE_16` indexing as used by the Mac mode helpers; changes there would break lookup semantics. The lack of include guards means repeated inclusion would be unsafe, though this local driver includes it once.

## Test Signals
Tests should validate that each non-NULL mode can round-trip through `mac_vmode_to_var()` and `valkyrie_var_to_par()`, that pitch zero blocks unsupported color depths, that VRAM calculations match expected line length times height, and that CONFIG_MAC versus non-CONFIG_MAC builds expose the intended mode set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/valkyriefb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vesafb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vesafb.c

## Purpose
`vesafb.c` provides the classic boot-time VESA linear framebuffer driver. It does not perform BIOS mode discovery or switching itself; it consumes the mode already selected by firmware/early boot and described in `screen_info`, maps the linear framebuffer, and registers an fbdev device.

## Important APIs, Types, And Functions
`struct vesafb_par` stores the pseudo palette, framebuffer resource base/size, write-combine cookie, and optional VGA I/O region. `vesafb_ops` supplies default iomem operations, destroy cleanup, colormap handling, and optional panning. Important helpers are `vesafb_setup()`, `vesafb_probe()`, `vesafb_destroy()`, `vesafb_setcolreg()`, `vesa_setpalette()`, and `vesafb_pan_display()`.

## Control Flow
The platform driver probes `vesa-framebuffer` devices supplied by sysfb. Probe copies `screen_info`, parses `video=vesafb:` options, verifies `VIDEO_TYPE_VLFB`, derives fix/var fields from LFB geometry and color component positions, calculates usable/remapped VRAM, reserves memory opportunistically, allocates `fb_info`, initializes PMI pointers if available, determines panning and palette support, maps the framebuffer with or without write combining, allocates the cmap, acquires the aperture, and registers the framebuffer. Destroy handles cmap, write-combine deletion, unmap, memory release, and `framebuffer_release()`.

## State And Persistence
The driver has static option state (`inverse`, `mtrr`, `vram_remap`, `vram_total`, `pmi_setpal`, `ypan`, PMI function pointers, depth, and VGA compatibility), plus per-device state in `vesafb_par`. Hardware state is mostly inherited from boot firmware. Runtime state is the mapped LFB, cmap, pseudo palette, and panning offsets.

## Dependencies And Integration Points
It depends on platform sysfb devices, `struct sysfb_display_info`, fbdev, VGA DAC I/O, x86 PMI when available, aperture ownership, resource reservation, and architecture write-combine helpers. Boot/module options control scrolling, palette backend, MTRR/write-combine behavior, and VRAM sizing.

## Risks
Because firmware selected the mode, the driver cannot recover from bad firmware geometry. `request_mem_region()` failure is non-fatal by design, which supports firmware quirks but weakens exclusivity. PMI calls are architecture-specific and unsafe if firmware reports unusable segments. Static globals make multiple instances conceptually fragile, although sysfb usage normally provides one device. The `inverse` option is parsed but not used in the visible code.

## Test Signals
Signals include successful probe on a `vesa-framebuffer` sysfb device, correct `/dev/fb*` geometry matching boot mode, valid cmap and pseudo-palette updates, panning only when PMI and virtual height allow it, aperture conflict behavior, mtrr/write-combine log behavior, and clean unregister through `vesafb_destroy()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vesafb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vfb.c

## Purpose
`vfb.c` implements a virtual framebuffer backed by vmalloc memory. It is useful for testing fbdev clients, fbcon behavior, drawing paths, and modes without physical display hardware.

## Important APIs, Types, And Functions
The driver registers a synthetic platform device/driver named `vfb` when explicitly enabled. `vfb_ops` uses default sysmem read/write/draw helpers plus `vfb_check_var()`, `vfb_set_par()`, `vfb_setcolreg()`, `vfb_pan_display()`, and `vfb_mmap()`. Static parameters are `videomemorysize`, `mode_option`, and `vfb_enable`. `get_line_length()` centralizes line pitch alignment.

## Control Flow
Initialization parses `video=vfb:` in built-in builds or module parameters, returns `-ENXIO` unless enabled, registers the platform driver, and creates a platform device. Probe allocates 32-bit user-addressable vmalloc memory, allocates `fb_info`, chooses a mode through `fb_find_mode()` with a 640x480 default, initializes fix/var/cmap/pseudo-palette state, registers the framebuffer, and computes line length. Remove unregisters the framebuffer and frees vmalloc memory, cmap, and `fb_info`.

## State And Persistence
The framebuffer contents persist only in the allocated `videomemory` until remove/module unload. Mode state lives in `fb_info->var` and `fix`, while the pseudo palette occupies the allocation area provided by `framebuffer_alloc()`. The driver stores no persistent external state.

## Dependencies And Integration Points
It depends on fbdev sysmem helpers, vmalloc memory mapping, platform devices, `fb_find_mode()`, and generic fbdev mmap support through `remap_vmalloc_range()`. It integrates with userspace through normal framebuffer APIs and supports `videomemorysize` and preferred mode options.

## Risks
Memory use is controlled by a module parameter and can fail at probe. `vfb_mmap()` maps `info->fix.smem_start`, which is set to the vmalloc pointer cast to an integer; correctness depends on `remap_vmalloc_range()` receiving that original vmalloc address. The code has a single static `videomemory`, so it is not structured for multiple devices. It intentionally has no hardware synchronization or acceleration.

## Test Signals
Signals include explicit enable/disable behavior, successful mode selection, `fbset` validation for 1/8/16/24/32 bpp, panning and ywrap bounds checking, mmap read/write visibility, drawing helper behavior, cmap/pseudo-palette updates, and clean remove without leaked vmalloc memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vga16fb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/vga16fb.c

## Purpose
`vga16fb.c` is an fbdev driver for legacy EGA/VGA 16-color graphics modes supplied by sysfb. It programs VGA sequencer, CRTC, graphics, attribute, DAC, and planar memory behavior directly, and supplies custom drawing paths for VGA planar framebuffers.

## Important APIs, Types, And Functions
`struct vga16fb_par` stores saved VGA state, a `vgastate`, refcount, blanking flags, mode flags, VGA/EGA distinction, misc/clock/palette state, and computed CRTC registers. The fbdev interface is `vga16fb_ops`, including open/release state save/restore, check/set mode, palette, pan, blank, fillrect, copyarea, imageblit, mmap, and destroy. Key helpers include low-level VGA register access wrappers, `vga16fb_check_var()`, `vga16fb_set_par()`, `vga16fb_update_fix()`, `vga16fb_clock_chip()`, `vga16fb_probe()`, and custom planar blitters.

## Control Flow
Probe is driven by `ega-framebuffer` or `vga-framebuffer` platform IDs and accepts only EGA/VGA graphics modes `0x0d`, `0x0e`, `0x10`, or `0x12`. It reserves/maps VGA memory, allocates `fb_info`, configures VGA/EGA palette depth, validates the default mode, acquires the aperture, registers the framebuffer, and stores driver data. A mode set computes CRTC register bytes in `check_var()`, then `set_par()` writes misc output, sequencer, CRTC, graphics controller, and attribute controller registers in the required reset/unreset sequence. Drawing operations switch VGA write modes, set/reset, masks, and data rotate registers to implement fills, copies, and image expansion.

## State And Persistence
The driver saves VGA fonts, mode, and cmap on first open and restores them on last release. Runtime state includes CRTC arrays, blanked palette/vesa flags, mode flags, and hardware registers. Framebuffer memory is the fixed VGA aperture. No disk state is used.

## Dependencies And Integration Points
It depends on sysfb platform devices, VGA I/O helpers from `<video/vga.h>`, aperture ownership, raw I/O port access, fbdev cfb fallback helpers, and legacy VGA memory mapping. It integrates with fbcon and other fbdev users, but comments note that VGA regions are shared with vgacon/others rather than fully exclusive.

## Risks
VGA planar programming is register-order-sensitive and hardware-clone-sensitive. Some clipping paths assume widths aligned to multiples of 8, reflected in pixmap capabilities. Resource sharing with vgacon is incomplete. Save/restore relies on balanced open/release refcounts. The driver rejects many modern or firmware modes, and direct port I/O makes it architecture/platform constrained.

## Test Signals
Signals include probe rejection for unsupported `screen_info`, successful 640x480/4 registration, `fbset` mode validation boundaries, correct palette programming on EGA and VGA, blank/unblank restoring sync registers, custom fill/copy/imageblit rendering in planar modes, state restoration after last close, and clean unregister with memory unmap/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/vga16fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/Makefile

## Purpose
This Makefile defines how the VIA framebuffer driver is built when `CONFIG_FB_VIA` is enabled. It links a single `viafb.o` module/object from the core fbdev file, hardware programming files, output-device helpers, acceleration, mode tables, VIA core helpers, and AUX/I2C encoder support.

## Important APIs, Types, And Functions
There are no C APIs in this file. Its important build contract is `obj-$(CONFIG_FB_VIA) += viafb.o` and the `viafb-y := ...` object list. The list includes `viafbdev.o`, `hw.o`, `via_i2c.o`, `dvi.o`, `lcd.o`, `ioctl.o`, `accel.o`, `global.o`, `viamode.o`, `via_clock.o`, GPIO/core files, modesetting, and multiple AUX encoder implementations.

## Control Flow
Kbuild evaluates the config-gated object line. When enabled, all objects in `viafb-y` are compiled and linked into the composite `viafb.o`. Ordering is mostly link ordering; runtime initialization is still governed by the C files' init paths and function calls.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is the build graph and which object files become part of the VIA fbdev driver.

## Dependencies And Integration Points
It integrates with Linux kbuild and the `CONFIG_FB_VIA` Kconfig symbol. Because it aggregates many helper files, missing or misordered entries would surface as unresolved symbols or absent runtime support for DVI, LCD, acceleration, I2C, AUX encoders, or mode tables.

## Risks
The broad object list means build failures can arise from optional-looking functionality that is actually always linked when `CONFIG_FB_VIA` is enabled. The file does not express finer-grained config around individual encoders or acceleration helpers. Build-only changes here can alter the driver's symbol availability and runtime feature set.

## Test Signals
Primary signals are successful `make drivers/video/fbdev/via/` or kernel builds with `CONFIG_FB_VIA=y/m`, absence of unresolved symbols, and a resulting `viafb.o` containing expected helper symbols such as `viafb_setmode`, `viafb_dvi_enable`, and `viafb_setup_engine`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.c

## Purpose
`accel.c` initializes and drives VIA Unichrome 2D acceleration resources: hardware bitblt, virtual queue setup, cursor memory reservation, cursor visibility, and engine-idle synchronization.

## Important APIs, Types, And Functions
Exports within the VIA driver are `viafb_setup_engine()`, `viafb_reset_engine()`, `viafb_show_hw_cursor()`, and `viafb_wait_engine_idle()`. Internal helpers `hw_bitblt_1()` and `hw_bitblt_2()` program older and newer 2D register layouts, while `viafb_set_bpp()` writes GEMODE bpp bits. The implementation relies on shared `viafb_par`, `viafb_shared`, chip information, `engine_mmio`, and `hw_bitblt` function pointer state.

## Control Flow
Engine setup validates MMIO, selects the proper bitblt implementation by graphics chip generation, reserves tail framebuffer memory for cursor and virtual queue, optionally reserves camera framebuffer memory, then resets the engine. Bitblt validates operation, bpp, coordinates, dimensions, pitch, and address alignment, sets direction bits for overlapping framebuffer copies, writes source/destination/dimension/color/pitch registers, starts the blit command, and streams system-memory source data through the MMIO blit aperture if needed. Reset clears engine registers, initializes AGP/transaction and virtual queue registers with generation-specific sequences, and programs cursor base registers.

## State And Persistence
State persists in `viapar->shared`: selected `hw_bitblt` function, cursor and VQ VRAM addresses, camera offsets, and chip information. Hardware state persists in engine MMIO registers until reset or modeset. `fbmem_free` and `fbmem_used` are mutated to reserve memory regions.

## Dependencies And Integration Points
It depends on `accel.h` register definitions, `chip.h` chip IDs, `via-core` MMIO mapping, and shared VIA fbdev structures from `global.h`/`viafbdev.h`. It is called by the main VIA fbdev setup path and supports higher-level accelerated drawing/cursor code.

## Risks
The bitblt functions reject unsupported alignment and size encodings but do not recover from all hardware hangs. Engine reset sequences are magic-number heavy and chip-generation-specific. Memory reservation is a simple top-of-framebuffer subtraction without a general allocator, so feature additions can collide if ordering changes. `viafb_wait_engine_idle()` busy-waits up to `MAXLOOP` and only logs on timeout.

## Test Signals
Signals include successful acceleration setup with a non-NULL `hw_bitblt`, correct framebuffer memory accounting, cursor memory not overlapping visible buffers, bitblt fill/copy/mono operations across supported bpp values, timeout-free idle waits, and chip-matrix testing for H2, H5, and M1 engine variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.h

## Purpose
`accel.h` defines VIA framebuffer acceleration constants, MMIO register offsets, command bits, status masks, memory reservation sizes, and public acceleration helper prototypes.

## Important APIs, Types, And Data
Important definitions include `FB_ACCEL_VIA_UNICHROME`, VGA MMIO base offsets, cursor and virtual queue sizes, 2D engine register offsets for legacy and M1 layouts, GEMODE bpp encodings, GECMD command bits, source/destination mode bits, clipping/pattern/mono flags, status masks for H2/H5/M1 engines, `MAXLOOP`, and bitblt operation IDs. It declares `viafb_setup_engine()`, `viafb_reset_engine()`, `viafb_show_hw_cursor()`, and `viafb_wait_engine_idle()`.

## Control Flow
The header has no control flow. Its constants are consumed by `accel.c` to program registers and by other VIA fbdev files to advertise acceleration and manage cursor state.

## State And Persistence
No runtime state is stored here. The constants define persistent ABI-like assumptions inside the driver about MMIO layout, command encodings, and reserved framebuffer memory sizes.

## Dependencies And Integration Points
It is included through `global.h` and therefore becomes part of most VIA fbdev compilation units. It integrates `accel.c` with chip detection and main fbdev setup code via shared prototypes and constants.

## Risks
Incorrect register offsets or masks can hang the 2D engine or corrupt framebuffer memory. The fixed `CURSOR_SIZE` and `VQ_SIZE` constants affect framebuffer memory layout. Because several chip families reuse names with different register layouts, callers must pair the constants with the right engine type.

## Test Signals
Signals include clean compilation across all VIA objects, correct register writes visible in MMIO traces, successful cursor and VQ allocation sizes, and acceleration tests on chips using both legacy and M1 register maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/chip.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/chip.h

## Purpose
`chip.h` defines VIA Unichrome chip IDs, revisions, transmitter IDs, bus/interface constants, and shared information structures that describe graphics, TMDS, LVDS, and pad-driving configuration.

## Important APIs, Types, And Data
Key constants include the VIA PCI vendor ID, `UNICHROME_*` chip names and PCI device IDs, CLE266/CX700 revisions, TMDS/LVDS transmitter IDs and I2C addresses, and data-width flags. Core structures are `tmds_chip_information`, `lvds_chip_information`, `enum via_2d_engine`, `chip_information`, `tmds_setting_information`, `lvds_setting_information`, `GFX_DPA_SETTING`, and `VT1636_DPA_SETTING`.

## Control Flow
This header has no executable control flow. `hw.c`, `dvi.c`, `lcd.c`, and acceleration setup use its constants to branch by chip family and fill shared configuration structs.

## State And Persistence
The structure definitions shape persistent runtime state stored in `viaparinfo->chip_info` and related setting pointers. The header itself does not allocate state.

## Dependencies And Integration Points
It includes `global.h`, which makes this a cyclic-looking but established local include relationship. Its structures are central integration points between chip probing, DVI/LVDS detection, mode setting, acceleration selection, and pad-drive tuning.

## Risks
The header is a single source of truth for many hardware IDs. A wrong ID or output-interface interpretation will route mode programming to the wrong registers. The include of `global.h` from `chip.h` increases coupling and makes isolated reuse difficult. Several structures use `int` for hardware enums rather than strongly typed enums, so invalid values can flow until checked in register-writing code.

## Test Signals
Signals include correct chip-family detection, expected 2D engine enum selection, successful TMDS/LVDS identification using declared I2C addresses, and build coverage for all files that consume `chip_information`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/debug.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/debug.h

## Purpose
`debug.h` provides compile-time debug and warning print macros for the VIA framebuffer driver.

## Important APIs, Types, And Data
The header defines `VIAFB_DEBUG` and `VIAFB_WARN` switches, plus `DEBUG_MSG()` and `WARN_MSG()` macros. When enabled, the macros call `printk`; when disabled, they call `no_printk`, preserving format checking while avoiding runtime output.

## Control Flow
There is no runtime control flow beyond macro expansion. Call sites in VIA source files compile either to logging calls or to `no_printk` stubs depending on the constants.

## State And Persistence
No runtime state is stored. The file controls build-time logging behavior only.

## Dependencies And Integration Points
It includes `<linux/printk.h>` and is included by `global.h`, making the macros available broadly across VIA fbdev files.

## Risks
Both debug and warning switches default to `0`, so even `WARN_MSG()` call sites are suppressed unless the header is edited. This can hide diagnostics that might otherwise be expected in warning scenarios. Conversely, enabling the macros globally could produce noisy kernel logs from register-heavy paths.

## Test Signals
Signals are compile-time: format warnings should still be caught through `no_printk`, enabling either macro should produce expected log output, and disabled builds should not emit runtime messages from `DEBUG_MSG()`/`WARN_MSG()` call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.c

## Purpose
`dvi.c` handles VIA DVI/TMDS transmitter identification, connector sensing, EDID-based panel limits, DVI timing setup, and DVI output enable/disable register programming.

## Important APIs, Types, And Functions
Public VIA-driver functions are `viafb_init_dvi_size()`, `viafb_tmds_trasmitter_identify()`, `viafb_dvi_set_mode()`, `viafb_dvi_sense()`, `viafb_dvi_disable()`, and `viafb_dvi_enable()`. Internal helpers wrap TMDS I2C access, query EDID, parse EDID monitor descriptor pixel-clock limits, and apply chip-specific skew patches for DVP0/DFP-low outputs.

## Control Flow
TMDS identification temporarily enables output pads, probes VT1632 over candidate I2C ports, initializes it when found, otherwise treats CX700 DVI layouts as integrated TMDS or restores pad registers and marks no transmitter. DVI sensing powers/controls pads, reads VT1632 hotplug status, falls back to EDID probing, then restores saved registers. Mode setup optionally switches to a reduced-blanking mode if EDID-derived max pixel clock would be exceeded, then delegates CRTC timing programming to `viafb_fill_crtc_timing()`. Enable/disable branches by output interface and chip family to power TMDS, route pads, clear direct-display-period bits, and apply skew fixes.

## State And Persistence
State is stored in global/shared VIA structures reachable through `viaparinfo`: TMDS chip name, target I2C address, I2C port, output interface, active timing, max pixel clock, and IGA path. Hardware register changes persist until restored or overwritten by later modeset/output changes.

## Dependencies And Integration Points
It depends on `linux/via-core.h`, `linux/via_i2c.h`, VIA register helpers from `global.h`, chip definitions from `chip.h`, DVI constants from `dvi.h`, mode helpers from `viamode.h`, and timing programming in `hw.c`. It is called during chip initialization, hotplug/sense paths, and full modesets.

## Risks
The code is global-state-heavy and assumes `viaparinfo` and nested pointers are initialized. EDID probing temporarily changes the TMDS I2C target to `0xA0`; one failure path in `viafb_dvi_query_EDID()` returns false without restoring the saved target, which can poison later TMDS register accesses. Many register sequences are chip-specific and magic-number based. The function name `viafb_tmds_trasmitter_identify` carries the historical typo and must be matched by callers.

## Test Signals
Signals include VT1632 detection on both I2C ports, integrated TMDS detection on CX700 DVI layouts, EDID max-pixel-clock extraction, DVI sense hotplug state, reduced-blanking fallback when pixel clock is too high, correct enable/disable register traces per interface, and regression coverage for restoring TMDS target address after failed EDID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.h

## Purpose
`dvi.h` defines DVI/TMDS constants and declares the DVI helper functions used by the VIA framebuffer driver.

## Important APIs, Types, And Data
Constants include VT1632 device ID register/value, panel-size source constants, DVI panel ID values, EDID version markers, and connection type flags for DVI/HDMI. Function declarations cover sensing, enable/disable, TMDS transmitter identification, panel-size initialization, and DVI mode programming.

## Control Flow
There is no executable control flow. `dvi.c` implements the declared functions and consumes the constants during transmitter detection and EDID parsing.

## State And Persistence
No state is stored here. The header defines stable constants that shape runtime state in `tmds_chip_information` and `tmds_setting_information`.

## Dependencies And Integration Points
The prototypes rely on structures declared in `chip.h`/`global.h` and on `struct fb_var_screeninfo` from fbdev headers included through the VIA global include chain. It integrates `dvi.c` with `hw.c` and other VIA display selection code.

## Risks
The typo `GET_DVI_SZIE_BY_HW_STRAPPING` is part of the local API spelling and can be propagated. Panel ID constants are narrow and do not describe arbitrary EDID modes. Any mismatch between this header and `dvi.c` would break the composite `viafb.o` build.

## Test Signals
Signals include clean compilation of all callers, correct VT1632 detection using the defined ID, and runtime paths that call each declared public function during DVI probe/sense/modeset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/dvi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.c

## Purpose
`global.c` defines the VIA framebuffer driver's cross-file global configuration and object pointers.

## Important APIs, Types, And Data
It defines display layout and feature globals such as `viafb_platform_epia_dvi`, `viafb_device_lcd_dualedge`, `viafb_bus_width`, `viafb_display_hardware_layout`, `viafb_DeviceStatus`, hotplug mode fields, refresh rates, LCD method/mode, output enable flags, SAMM/dual-fb flags, primary device selection, LCD panel ID, and global `fb_info`/`viafb_par` pointers for primary and secondary framebuffers.

## Control Flow
There is no executable control flow. Other VIA files read and mutate these globals during option parsing, chip initialization, mode setting, hotplug handling, DVI/LCD setup, and framebuffer registration.

## State And Persistence
These globals are process/kernel lifetime state for the VIA fbdev driver. They provide defaults before probe and become shared mutable runtime state after initialization. No external persistence is performed.

## Dependencies And Integration Points
The file includes `global.h`, so the definitions match declarations consumed across `hw.c`, `dvi.c`, `lcd.c`, `viafbdev.c`, `ioctl.c`, and related helpers.

## Risks
Global mutable state makes ordering important and complicates multi-device support. Many fields are plain `int` flags with implicit enum domains. Hotplug and modeset code must coordinate updates carefully because settings such as `viafb_DVI_ON`, `viafb_LCD_ON`, `viafb_SAMM_ON`, and `viafb_primary_dev` drive hardware routing.

## Test Signals
Signals include default startup configuration, option parsing changing expected globals, modeset paths updating hotplug fields, dual framebuffer scenarios using `viafbinfo1`/`viaparinfo1`, and absence of stale globals across module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.h

## Purpose
`global.h` is the umbrella include for the VIA framebuffer driver. It gathers kernel headers and VIA local headers so source files share common types, register helpers, chip structures, mode tables, LCD/DVI APIs, ioctl definitions, and utility declarations.

## Important APIs, Types, And Data
The file includes fbdev, PCI, I/O, proc, console, timer, optional OLPC detection, and VIA local headers: `debug.h`, `viafbdev.h`, `chip.h`, `accel.h`, `share.h`, `dvi.h`, `viamode.h`, `hw.h`, `lcd.h`, `ioctl.h`, `via_utility.h`, `vt1636.h`, and `tblDPASetting.h`. It also provides a fallback `machine_is_olpc(x) 0` when OLPC support is not enabled.

## Control Flow
There is no direct control flow. Its include ordering controls what declarations and macros are visible to each VIA compilation unit.

## State And Persistence
No state is defined in the header itself in the viewed contents; state declarations and definitions live in included headers and `global.c`.

## Dependencies And Integration Points
This header is a major coupling point: most VIA files include it instead of selecting narrow dependencies. It integrates Linux subsystem headers with the VIA driver's private APIs and hardware tables.

## Risks
The umbrella pattern increases rebuild scope and makes dependency cycles harder to reason about, especially because `chip.h` includes `global.h`. The fallback `machine_is_olpc(x)` macro hides OLPC-specific behavior in non-OLPC builds. Header changes can have broad impact across all VIA objects.

## Test Signals
Signals include clean compilation of every VIA object, no missing declarations when local headers change, correct OLPC conditional behavior, and include-cycle changes detected by incremental builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.c

## Purpose
`hw.c` is the central VIA framebuffer hardware programming file. It manages chip initialization, output routing, display device state, palette setup, FIFO/fetch timing, PLL clock selection, CRTC timing, full modeset sequencing, and several user-facing output-device parse/format helpers.

## Important APIs, Types, And Functions
Externally used functions include `viafb_lock_crt()`, `viafb_unlock_crt()`, `viafb_set_iga_path()`, `via_set_source()`, `via_set_state()`, `via_set_sync_polarity()`, `via_parse_odev()`, `via_odev_to_seq()`, `viafb_load_reg()`, `viafb_write_regx()`, `viafb_load_fetch_count_reg()`, `viafb_load_FIFO_reg()`, `viafb_set_vclock()`, `var_to_timing()`, `viafb_fill_crtc_timing()`, `viafb_init_chip_info()`, `viafb_update_device_setting()`, `viafb_init_dac()`, `viafb_setmode()`, `viafb_get_refresh()`, `viafb_set_dpa_gfx()`, and `viafb_fill_var_timing_info()`. Static tables define PLL limits, common VGA registers, FIFO register bitfields, palette LUT values, and output-device name mappings.

## Control Flow
Chip initialization sets clock operations, identifies graphics revision and 2D engine, detects TMDS/LVDS, initializes display sizes/interfaces, assigns IGA paths, and copies LCD display-method defaults. A full modeset powers screens/devices off, disables outputs, initializes common VGA and chip-specific extended registers, applies patches, sets primary/secondary pitch and depth, routes output devices to IGA1/IGA2, prepares second-channel state, fills CRTC timing for CRT/DVI/LCD outputs, applies CX700 display-channel selection, records hotplug defaults, re-enables outputs, sets sync polarity, enables PLL/clock state for active IGAs, powers devices back on, and unblanks the screen.

## State And Persistence
The file mutates shared global VIA state through `viaparinfo`, `viafbinfo`, `viafbinfo1`, output enable flags, hotplug fields, chip info, TMDS/LVDS setting structures, and clock function state. Hardware state persists in sequencer/CRTC/graphics/attribute registers, DAC LUTs, PLL registers, and output pad state.

## Dependencies And Integration Points
It depends on `global.h`, `via_clock.h`, mode/register tables from VIA headers, DVI and LCD helper modules, OLPC detection, fbdev timing structures, and low-level VIA register helpers. It is the integration hub between user-selected fb modes, chip detection, DVI/LCD modules, acceleration clock requirements, and actual register programming.

## Risks
The code is register-table and magic-number heavy, with many chip-family branches and global flags. Multiple output configurations interact through IGA assignment, SAMM/dual-fb state, and primary-device selection. Invalid global state can route outputs to the wrong IGA or write inappropriate registers. PLL calculation selects nearest limits but depends on correct per-chip tables. Several helpers silently ignore unsupported states after logging or returning, which can leave partial hardware state.

## Test Signals
Signals include chip/revision detection for each supported family, correct 2D engine enum selection, output-device parsing/printing, IGA assignment for CRT/DVI/LCD/LCD2 combinations, FIFO/fetch register programming for representative resolutions, PLL frequency accuracy, mode setting for single and SAMM/dual-fb configurations, DVI/LCD enable ordering, sync polarity correctness, hotplug field updates, and visual/panel tests across CLE266 through VX900 families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.c -->
