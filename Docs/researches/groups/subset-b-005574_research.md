# subset-b-005574 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.c

## Purpose
`sh_mobile_lcdcfb.c` is the fbdev driver for the SuperH Mobile LCDC display controller. It owns platform-data driven setup for main/sub LCD channels, optional overlays, backlight callbacks, panel/transmitter handoff, DMA-backed framebuffer memory, one-shot system-bus panels, runtime/system PM, and the fbdev operations exposed to userspace.

## Important APIs, types, and functions
Core private types are `struct sh_mobile_lcdc_priv`, `struct sh_mobile_lcdc_overlay`, `struct sh_mobile_lcdc_chan` from the companion header, and `struct sh_mobile_lcdc_format_info`. Register helpers include `lcdc_write`, `lcdc_read`, `lcdc_write_chan`, `lcdc_write_chan_mirror`, `lcdc_write_overlay`, and `lcdc_wait_bit`. Lifecycle paths are `sh_mobile_lcdc_probe`, `sh_mobile_lcdc_remove`, `sh_mobile_lcdc_start`, `__sh_mobile_lcdc_start`, `sh_mobile_lcdc_stop`, suspend/resume callbacks, and runtime PM callbacks. Fbdev entry points include main-channel `sh_mobile_lcdc_ops` and overlay `sh_mobile_lcdc_overlay_ops`, covering mode validation, set_par, pan, blank, mmap, ioctl `FBIO_WAITFORVSYNC`, drawing hooks, open/release accounting, and pseudo-palette setup.

## Control flow
Probe requires platform data, maps MMIO, requests the IRQ, validates each channel interface, attaches optional backlight and transmitter devices, chooses main/sub register offset tables, sets a forced FOURCC for dual-channel LCDC, allocates coherent DMA framebuffers, initializes fb_info structures, initializes overlays, starts hardware, then registers channel and overlay framebuffers. Start enables clocks for active channels, resets the controller, calls board panel `setup_sys` hooks, computes DMA base addresses and chroma offsets, programs overlays, configures channel geometry/format/pitch/timing, starts dot clocks and output, enables deferred I/O for one-shot system-bus panels, turns display devices on, and powers backlights. Stop flushes deferred I/O, waits for frame-end in one-shot mode, powers backlights off, disables external displays, stops the LCDC, and drops clock/runtime-PM references.

## State and persistence
All state is runtime kernel state. `struct sh_mobile_lcdc_priv` tracks MMIO base, IRQ, clock, runtime PM use count, channel array, overlay array, started state, and dual-channel forced format. Channels and overlays cache DMA buffers, current format, resolution, virtual resolution, pitch, pan offset, base Y/C addresses, and fb_info pointers. Channels also track open use count, deferred-I/O scatterlists, frame-end wait state, vsync completion, backlight state, display mode, and blank state. Hardware registers and external panel/backlight state persist only until driver reprogramming, suspend, remove, or reset.

## Dependencies and integration points
The file integrates with Linux fbdev, fbcon, backlight core, DMA coherent allocation/mmap, platform devices and platform data from `<video/sh_mobile_lcdc.h>`, clocks, runtime PM, interrupt handling, V4L2 FOURCC/color-space constants, deferred I/O, and optional transmitter devices implementing `sh_mobile_lcdc_entity_ops`. Board-specific panel callbacks (`setup_sys`, `start_transfer`, `display_on`, `display_off`) are central integration points for system-bus and external display hardware.

## Risks and test signals
Risk areas include unbounded busy-wait loops on hardware status bits, clock/runtime-PM reference balance around interrupts and deferred I/O, dual-channel FOURCC coupling, YUV chroma offset math, mode memory-size overflow assumptions, error unwinding through `sh_mobile_lcdc_remove`, sysfs overlay updates racing display programming, and panel callback failures after clocks are enabled. Test signals include boot/probe on main-only and main+sub configurations, invalid interface and mode rejection, RGB and NV12/NV16/NV24 panning, `FBIO_WAITFORVSYNC` timeout behavior, deferred-I/O one-shot panel flushes, blank/unblank clock transitions, overlay enable/disable plus alpha/ROP3/position sysfs writes, suspend/resume, runtime PM, and remove after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.h

## Purpose
`sh_mobile_lcdcfb.h` is the private header shared by the SH Mobile LCDC fbdev implementation and related transmitter/panel glue. It defines per-channel register identifiers, display entity callbacks/events, and the channel state structure consumed by the C driver and platform callbacks.

## Important APIs, types, and functions
The register enum names channel-local LCDC registers from `LDDCKPAT1R` through `LDHAJR`, with `NR_CH_REGS` sizing the offset arrays in the C file. `PALETTE_NR` fixes the pseudo-palette size at 16. `struct sh_mobile_lcdc_entity_ops` provides `display_on` and `display_off` callbacks for an attached transmitter/display entity. `enum sh_mobile_lcdc_entity_event` names connect, disconnect, and mode events. `struct sh_mobile_lcdc_entity` stores module ownership, ops, backpointer to the owning channel, and a default mode. `struct sh_mobile_lcdc_chan` is the central per-display-channel state object.

## Control flow
The header itself has no executable control flow. At runtime, `sh_mobile_lcdcfb.c` allocates channels inside `struct sh_mobile_lcdc_priv`, fills `cfg`, `reg_offs`, `enabled`, display mode, DMA buffer, and fb_info fields during probe, and then passes channel pointers to fbdev callbacks, panel callbacks, system-bus transfer callbacks, backlight callbacks, interrupt wakeups, and transmitter display operations.

## State and persistence
`struct sh_mobile_lcdc_chan` carries runtime-only state: platform configuration, register offset table, cached `LDMT1R` interface value, enable bit, open use count protected by `open_lock`, framebuffer memory and DMA address, panning/base-address values for luma/chroma, frame-end wait state, vsync completion, format/colorspace/resolution/pitch, backlight device and brightness cache, fb_info, pseudo-palette, selected display mode, deferred-I/O state, scatterlist, and blank status. None of this is persisted outside the driver lifetime.

## Dependencies and integration points
The header depends on Linux completion, fbdev, mutex, wait queues, DMA address types through included fb/platform context, and forward declarations for backlight, module, channel/entity/format/private structures. It integrates platform definitions from `<video/sh_mobile_lcdc.h>` indirectly through `cfg` pointers and is consumed by the C driver plus board/panel callbacks that operate on `struct sh_mobile_lcdc_chan`.

## Risks and test signals
Risks are mostly ABI/structure-coupling risks inside the driver: `reg_offs` must match `NR_CH_REGS`, callbacks must tolerate `tx_dev->lcdc` being cleared on remove, deferred-I/O and frame-end fields must be initialized before use, and platform callbacks must not assume persistent framebuffer addresses across probe failures or remove. Test signals are successful compile coverage for the driver and board files, probe/remove with transmitter devices, deferred-I/O panels, vsync waits, backlight registration, and panning paths that exercise both RGB and YUV base-address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/simplefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/simplefb.c

## Purpose
`simplefb.c` implements the generic simple framebuffer platform driver. It binds firmware-provided framebuffer memory described by device tree or platform data, maps it write-combined, registers a minimal packed-pixel fbdev, and keeps clocks, regulators, and power domains enabled until a native graphics driver removes the conflicting aperture.

## Important APIs, types, and functions
Important data structures are `struct simplefb_par`, `struct simplefb_params`, `simplefb_fix`, `simplefb_var`, and the format table initialized from `SIMPLEFB_FORMATS`. Fbdev operations are `simplefb_setcolreg` and `simplefb_destroy` inside `simplefb_ops` using default IOMEM operations. Parsing functions are `simplefb_parse_dt` and `simplefb_parse_pd`. Resource-retention helpers are `simplefb_clocks_get/enable/destroy`, `simplefb_regulators_get/enable/destroy`, and `simplefb_attach_genpds`/`simplefb_detach_genpds`. Platform lifecycle is `simplefb_probe`, `simplefb_remove`, and the `simple-framebuffer` OF match table.

## Control flow
Probe exits if the `simplefb` fb option disables the driver, parses width/height/stride/format from platform data or device tree, prefers `memory-region` over `reg` when present, reserves the framebuffer region when possible, allocates `fb_info`, fills fixed and variable screen info, maps framebuffer memory with `ioremap_wc`, obtains optional clocks/regulators/power domains, enables retained resources, acquires an aperture for platform-device handoff, and registers the framebuffer. Remove unregisters the framebuffer; the fbdev destroy path disables retained resources, detaches power domains, unmaps memory, releases the fb_info, and releases the memory region if it was actually reserved.

## State and persistence
Driver state is per-framebuffer runtime state in `struct simplefb_par`: pseudo-palette, physical base/size, optional reserved resource, optional clock array and enable flag, optional genpd devices/links, and optional regulators plus enable flag. The framebuffer memory contents are firmware/native-display memory and may outlive the driver, but the driver's mappings and resource references do not persist after unregister/destroy.

## Dependencies and integration points
The driver depends on fbdev, platform devices, OF parsing, reserved memory, clock framework, regulator framework, PM generic domains, aperture helpers, and `linux/platform_data/simplefb.h`. Its most important integration point is sysfb/firmware handoff: `devm_aperture_acquire_for_platform_device` lets later DRM or native fbdev drivers remove `simplefb` when they need the same display memory.

## Risks and test signals
Risks include accepting inconsistent firmware stride/size/format data, mapping an unreserved memory region when `request_mem_region` fails, partial resource acquisition with nonfatal missing clocks/regulators, release-order mistakes between fbdev destroy and platform remove, and aperture overlap errors during native-driver handoff. Test signals include DT and platform-data probe, supported and unsupported format strings, `memory-region` versus `reg` precedence, missing optional clocks/regulators, `-EPROBE_DEFER` handling, multi-power-domain attach/detach, framebuffer color register writes, native DRM handoff through aperture removal, and remove/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/simplefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/300vtbl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/300vtbl.h

## Purpose
`300vtbl.h` is a static register and timing table catalog for the SiS 300-series framebuffer initialization code. It supplies mode IDs, reference timing indices, CRTC register values, memory/video clocks, sequencer defaults, LCD/LVDS/CRT2 bridge tables, Chrontel TV encoder tables, and panel-specific timing descriptors for chips such as SiS 300/305/540/630/730.

## Important APIs, types, and functions
The header defines data, not functions. Major table families are `SiS300_EModeIDTable`, `SiS300_RefIndex`, `SiS300_VBModeIDTable`, `SiS300_CRT1Table`, `SiS300_MCLKData_630`, `SiS300_MCLKData_300`, mutable `SiS300_VCLKData`, `SiS300_SR15`, `SiS300_PanelDelayTbl`, LCD timing tables for 1024x768 and 1280x1024, `SiS300_CRT2Part2_1024x768_*`, BARCO and 848x480 LVDS data, Chrontel PAL/NTSC/SVIDEO overscan data, `SiS300_PanelType04_*`, Chrontel slave CRTC tables, Chrontel register tables, and Chrontel VCLK selector arrays. The structures are declared in the SiS init headers and referenced through pointers in `struct SiS_Private`.

## Control flow
There is no direct control flow in the header. `init.c` includes it under `CONFIG_FB_SIS_300`; `InitTo300Pointer()` assigns these arrays into `SiS_Pr` function-state pointers after chip detection. Later mode-setting code indexes the tables by BIOS-like mode IDs, reference indices, panel type, TV standard, bridge type, and chip type to program CRT1, CRT2, memory clocks, video clocks, LCD scaling, LVDS timing, and TV encoder registers.

## State and persistence
Most arrays are `static const` and are effectively immutable build-time state embedded in the driver. `SiS300_VCLKData` is non-const, matching the broader SiS init code's expectation that VCLK tables can be patched or treated through mutable pointers. No runtime persistence exists beyond the in-memory driver image and the hardware registers programmed from these values.

## Dependencies and integration points
The header depends on structure definitions and constants from `init.h`, `initdef.h`, `vstruct.h`, and related SiS headers. It is tightly integrated with `init.c` pointer initialization and `init301.c` CRT2/LVDS/TV programming. Build inclusion is gated by `CONFIG_FB_SIS_300`, while `drivers/video/fbdev/sis/Makefile` links the common SiS init objects into `sisfb.o` when `CONFIG_FB_SIS` is enabled.

## Risks and test signals
Risks are table-index drift, sentinel mistakes, incorrect chip-family selection, mode IDs that disagree with shared `ModeIndex_*` arrays, mutable VCLK data assumptions, and hard-to-review numeric register regressions. Several entries encode legacy or panel-specific quirks, so small numeric changes can break only one output path. Test signals include compile coverage with `CONFIG_FB_SIS_300`, mode-set tests across 8/16/32 bpp, CRT1-only and CRT2 clone modes, LVDS panels including BARCO/848x480 cases, Chrontel NTSC/PAL/SVIDEO variants, suspend/resume mode restore, and comparing programmed registers against known-good hardware or BIOS traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/300vtbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/310vtbl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/310vtbl.h

## Purpose
`310vtbl.h` is the static register and timing table catalog for the SiS 315/330/340-era and related XGI framebuffer initialization path. It extends the 300-series table model with newer modes, more chip-specific memory-clock tables, separate bridge VCLK data, LVDS panel delays, widescreen modes, and PAL-M/PAL-N Chrontel TV variants.

## Important APIs, types, and functions
The header defines data arrays only. Key tables include `SiS310_EModeIDTable`, `SiS310_RefIndex`, `SiS310_CRT1Table`, chip-specific `SiS310_MCLKData_0_*` tables for 315/650/330/660/760/761/340, `SiS310_MCLKData_1*` ECLK data, mutable `SiS310_VCLKData`, mutable `SiS310_VBVCLKData`, `SiS310_SR15`, standard and LVDS panel delay tables, LCD timing data, `SiS310_CRT2Part2_1024x768_1`, multiple Chrontel overscan data tables, Chrontel slave CRTC tables, Chrontel register tables for NTSC/PAL/PAL-M/PAL-N, and Chrontel VCLK selector arrays. The mode table covers legacy VGA resolutions plus newer widescreen modes such as 1280x800, 1680x1050, 1920x1080, and 960-wide panel modes.

## Control flow
The header has no executable path. `init.c` includes it under `CONFIG_FB_SIS_315`; `InitTo310Pointer()` selects tables based on `SiS_Pr->ChipType`, assigning the proper memory-clock table for 315, 550/650/740, 330, 661/741, 760, 761, or 340/XGI-class hardware. Subsequent mode setup indexes these arrays through `struct SiS_Private` pointers to program CRT1 timings, RAM clocks, dot clocks, bridge clocks, LVDS delays, LCD scaling, and TV encoder registers.

## State and persistence
The file contributes static driver data. Most tables are `static const`; `SiS310_VCLKData` and `SiS310_VBVCLKData` are mutable arrays because the SiS init code treats clock tables as runtime-adjustable data. The values persist only as part of the loaded driver and as programmed hardware register state after a mode set.

## Dependencies and integration points
The file depends on SiS structure definitions from the init headers and is coupled to pointer fields in `struct SiS_Private`. It integrates with `init.c` for chip-family pointer binding and with `init301.c` for bridge, LVDS, LCD, and Chrontel TV programming. Its availability is controlled by `CONFIG_FB_SIS_315`; the common `sisfb.o` link target includes the consuming init objects.

## Risks and test signals
Risks include selecting the wrong memory-clock table for a chip variant, breaking sentinel-terminated lookups, VCLK/VBVCLK mismatch for bridge modes, incorrect widescreen reference indices, stale comments around known Chrontel register inaccuracies, and regressions limited to PAL-M/PAL-N or LVDS paths. Test signals include `CONFIG_FB_SIS_315` build coverage, mode setting on each supported chip family when available, CRT1 and CRT2 output combinations, bridge-clock validation, widescreen and high-resolution modes, LVDS delay behavior, PAL/NTSC/PAL-M/PAL-N TV output, and register comparison against known-good tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/310vtbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/Makefile

## Purpose
This Makefile is the kbuild glue for the SiS framebuffer driver directory. It builds the `sisfb` composite object when `CONFIG_FB_SIS` is enabled.

## Important APIs, types, and functions
There are no C APIs in this file. The relevant kbuild declarations are `obj-$(CONFIG_FB_SIS) += sisfb.o` and `sisfb-objs := sis_main.o sis_accel.o init.o init301.o initextlfb.o`. These lines define both the config-controlled object and its component compilation units.

## Control flow
Kbuild evaluates `CONFIG_FB_SIS`; if enabled as built-in or module, it compiles the listed objects and links them into `sisfb.o`. Conditional content inside those objects, such as inclusion of `300vtbl.h` or `310vtbl.h`, is controlled by C preprocessor symbols like `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315` rather than by this Makefile.

## State and persistence
The file has no runtime state. Its only state is build graph state derived from `.config`, deciding whether the SiS framebuffer code is present and whether it is built-in or modular.

## Dependencies and integration points
It integrates the fbdev Kconfig symbol `CONFIG_FB_SIS` with the SiS driver sources. The component list ties the top-level fbdev driver (`sis_main.o`), acceleration (`sis_accel.o`), CRT1 init (`init.o`), CRT2/bridge init (`init301.o`), and external-LFB init support (`initextlfb.o`) into one driver.

## Risks and test signals
Risks are missing object components, stale file names, or a mismatch between Kconfig suboptions and conditionally compiled code in the listed objects. Test signals include `CONFIG_FB_SIS=y`, `CONFIG_FB_SIS=m`, 300-only and 315-only config builds, `make W=1` for the directory, and module load/link checks confirming that all referenced init and acceleration symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/Makefile -->
