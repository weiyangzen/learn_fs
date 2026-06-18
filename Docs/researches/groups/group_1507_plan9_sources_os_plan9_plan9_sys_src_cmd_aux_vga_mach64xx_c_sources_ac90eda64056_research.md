# Group Research: group_1507_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_vga_mach64xx_c_sources_ac90eda64056

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64xx.c

Implements the Plan 9 `aux/vga` controller backend for ATI Mach64/Rage-family adapters.

Key behavior:
- Defines Mach64 register indices, I/O-port and PCI-register addressing tables, PLL register access, LCD indexed access, and TV indexed access.
- `snarf()` detects ATI PCI devices, selects port or PCI register access, captures core registers, PLL state, optional LCD state, memory-size encoding, aperture size, and LT panel identity.
- `clock()` computes VCLK divisors, with special handling for active LCD panels where the existing BIOS-programmed PLL is preserved.
- `setdsp()` calculates Rage display FIFO/DSP timing from BIOS memory-clock tables, memory type, panel stretch state, video frequency, and depth.
- `init()` builds Mach64 CRTC, sync, pitch, pixel-depth, overlay, PLL, linear-aperture, LCD stretch, and DSP register state.
- `load()` unlocks registers, programs aperture, timing, LCD, DAC, DSP, PLLs, pixel width, and true-color palette ramp.
- `dump()` prints register/PLL/LCD state and decodes BIOS clock/LCD tables through `dumpmach64bios()`.

Important details:
- Uses `vga->private` as `Mach64xx`, shared with the hwgc stub.
- Linear mode is supported only when requested and usable; aperture alignment is forced to 16 MB.
- Depths above 8 require PCI-style register access.
- LCD handling intentionally avoids recomputing PLL clocks and instead uses panel/BIOS-derived values.
- BIOS parsing uses raw little-endian casts from `readbios()`, with explicit comments about endian dependence.

Filesystem relevance:
- Indirect but operational: participates in configuring Plan 9’s `#v` VGA/draw device through `aux/vga`, BIOS reads, and controller hooks used before `/dev/draw` initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/main.c

This is the main program for `aux/vga`, orchestrating VGA controller detection, mode lookup, register initialization, loading, and draw-device setup.

Key behavior:
- Parses flags for BIOS id, controller dump, software cursor, init, load, print, refresh, verbosity, monitor type, and alternate vgadb path.
- Reads `$vgactlr` and `$monitor`, falls back through vgadb controller probing, VESA probing, then generic VGA.
- Runs every controller’s `snarf`, `options`, `init`, `load`, and `dump` hooks through the linked controller chain.
- Resolves monitor modes from `/lib/vgadb`, `/env/<monitor>`, or VESA mode data.
- Handles physical and virtual screen sizes, including panning setup.
- Chooses default draw channel strings for common depths.
- Computes a mode frequency from video bandwidth and memory bandwidth when only bandwidth constraints are supplied.
- Configures kernel video state through `vgactlw("type")`, `linear`, `size`, `drawinit`, `hwgc`, `actualsize`, and `panning`.

Important details:
- `sequencer()` blanks/unblanks VGA output around hardware register programming.
- `linear()` negotiates and reads back the linear framebuffer aperture from `#v/vgactl`, supporting both old and newer `addr p ... size ...` formats.
- VESA loading is done before linear setup, then the type is switched back for acceleration.
- `rflag` protects refresh-only loads by checking the existing size unless explicitly overridden.
- A zero-byte write to `/dev/cursor` initializes cursor state after mode load.

Filesystem relevance:
- Directly controls Plan 9 device files and namespaces: `/lib/vgadb`, `/env`, `#v/vgactl`, `/dev/cursor`, and draw-device initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga2164w.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga2164w.c

Implements `aux/vga` support for Matrox Millennium/Millennium II MGA-2064W, MGA-2164W, and MGA-2164W AGP adapters with a TI TVP3026 RAMDAC.

Key behavior:
- Provides direct and indexed TVP3026 RAMDAC access via the Matrox control aperture.
- Provides CRTC-extension register access through `0x03DE`.
- `mapmga()` selects the kernel video driver type and attaches `mga2164wmmio` and `mga2164wscreen` segments.
- `snarf()` matches Matrox PCI IDs, maps MMIO/framebuffer regions, saves PCI option/device state, CRTC extensions, TVP registers, PCLK/MCLK/LCLK values, and probes installed VRAM.
- `options()` rounds `vga->virtx` up to a 128-pixel boundary.
- `clockcalc()` computes TVP3026 pixel-clock and loop-clock register triples.
- `init()` rejects depths above 8, computes VGA and Matrox CRTC-extension timing, RAMDAC mode registers, blanking fixes, memory option bits, and disables the generic VGA loader.
- `load()` programs Matrox extensions, PCI option state, VGA registers, TVP PLLs, loop clock, and RAMDAC registers in a strict order.
- `dump()` prints PCI, CRTC-extension, TVP, and clock registers.

Important details:
- Memory size is probed by writing sentinel bytes at odd-megabyte offsets and flushing the cache aperture.
- The implementation assumes “power graphics” Matrox mode and takes over load order from the generic VGA backend.
- Only 8-bit display modes are supported here.
- Several timing adjustments are documented as fixes over generic VGA vertical blanking behavior.

Filesystem relevance:
- Uses `#v/vgactl` and `segattach()` video segments, so it is tied to Plan 9’s video device namespace even though it is not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga2164w.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga4xx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga4xx.c

Implements `aux/vga` support for Matrox G200, G400/G450, and G550 adapters.

Key behavior:
- Defines Matrox PCI IDs, MMIO register offsets, VGA-compatible register windows, RAMDAC indexes, and many bit definitions for CRTC, sequencer, DAC, and pixel-clock control.
- Provides MMIO helpers for sequencer, CRTC, CRTC-extension, DAC, graphics-controller, attribute, and misc registers.
- `mapmga4xx()` sets video type `mga4xx` and attaches `mga4xxmmio` plus an 8 MB or 32 MB framebuffer segment.
- `snarf()` matches Matrox PCI devices, verifies memory-space enable, records revision/device data, maps apertures, and probes framebuffer size.
- `options()` aligns virtual width to 128 pixels.
- `g400_calcclock()` computes G200/G400 PLL settings; the G450/G550 path uses `G450Find*PLLParam`, sorted MNP candidates, lock probing, and fallback writes.
- `init()` validates depth/frequency, rejects interlace, computes detailed power-graphics timing fields, builds VGA/Matrox CRTC registers, computes byte/pixel scaling for 8/16/24/32 bpp, and disables generic VGA loading.
- `load()` sequences display blanking, CRTC2 off, cursor disable, pixel PLL setup, DAC setup, memory mapping, CRTC/extension programming, endian setup for 24/32 bpp, palette initialization, and cursor restoration.
- `dump()` emits register traces via `dump_all_regs()`.

Important details:
- G450/G550 PLL programming is lock-test driven and adapted from XFree86-era code.
- 24 bpp uses special offset and scale calculations; 32/24 bpp also set a big-endian mode register.
- `setpalettedepth()` writes `palettedepth` through `#v/vgactl`, but its string patching only handles one decimal digit cleanly.
- The file contains extensive debug traces and comments documenting historical fixes and supported acceleration assumptions.

Filesystem relevance:
- Directly uses `#v/vgactl` and named video segments exposed by the Plan 9 video device; not filesystem logic, but device-namespace dependent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga4xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/neomagic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/neomagic.c

Implements a simple NeoMagic laptop VGA backend for MagicGraph/MagicMedia chipsets.

Key behavior:
- `snarf()` runs generic VGA snarfing, unlocks NeoMagic extended registers, captures extended CRTC and graphics registers, matches PCI vendor `0x10C8`, and sets maximum clock, VRAM size, and aperture size by device ID.
- `options()` advertises linear framebuffer support.
- `init()` starts from generic VGA init, derives native panel size, configures LCD-only panel mode, centering/stretch controls, extended color mode, pitch, offsets, and palettes for 8/16/24 bpp.
- `load()` writes required NeoMagic extended registers around `generic.load()`, enables MMIO/linear flags, and loads a palette for non-8-bit modes.
- `dump()` prints generic VGA state plus captured NeoMagic extended CRTC/graphics registers.

Important details:
- Several device IDs are supported; older MagicGraph 128 variants are explicitly rejected.
- The switch that maps graphics register panel size lacks a `break` after the 1024x768 case, so that case falls through to 1280x1024.
- Hardware cursor controller `neomagichwgc` is only a named stub.
- The file calls itself a “fake” driver, reflecting narrow mode-setting support rather than full acceleration.

Filesystem relevance:
- Indirect: used by `aux/vga` to configure Plan 9 display devices and linear video memory, not filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/neomagic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/nvidia.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/nvidia.c

Implements `aux/vga` support for NVIDIA adapters from early NV4 through several NV4x-era families.

Key behavior:
- Maps NVIDIA MMIO and subdivides it into PFB, PRAMDAC, PEXTDEV, PMC, PTIMER, PFIFO, PRAMIN, PGRAPH, FIFO, and PCRTC register windows.
- `snarf()` finds NVIDIA display-class PCI devices, handles some PCI-X ID quirks, classifies architecture generation, detects crystal frequency, dual-head/two-stage PLL support, laptop LCD devices, framebuffer size, CRTC extension state, PLLs, dither, panel timing, and flat-panel dimensions.
- `clock()` searches PLL `m/n/p` values for single-stage and two-stage PLL families.
- `init()` rejects 24 bpp, handles optional `lcd=` mode attribute, computes hardware cursor placement, PLL values, CRTC overflow bits, blanking, LCD scaling flags, pixel depth, dual-head ownership, and cursor configuration.
- `load()` performs extensive device initialization: unlocks CRTC, initializes PMC/timer, framebuffer regions, PRAMIN object tables, PGRAPH state, PFIFO state, dual-head registers, LCD timing, CRTC extensions, PLL/DAC state, and final CRTC interrupt/display enable.
- `dump()` prints clock calculation, detected architecture/device IDs, CRTC extension state, PLLs, panel state, and dual-head flags.

Important details:
- Large blocks of register programming are architecture- and device-family-specific.
- Framebuffer size detection differs for NV4, nForce/nForce2 integrated devices, and later chips.
- LCD handling is partial and keyed by hard-coded device IDs plus mode attributes.
- The file includes NVIDIA-derived copyright text and is hardware-sensitive; errors in register tables can hang display hardware.

Filesystem relevance:
- Uses `#v/vgactl` type selection and `segattach("nvidiammio")`; it depends on Plan 9’s device namespace for hardware access.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/nvidia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/palette.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/palette.c

Implements the generic VGA palette controller for `aux/vga`.

Key behavior:
- `snarf()` reads pixel mask, DAC status, and all 256 RGB palette entries from VGA DAC ports.
- `init()` creates a default palette: color-cube style entries for 8-bit modes and grayscale entries for lower depths.
- `load()` writes the pixel mask and all palette entries back to DAC registers.
- `dump()` prints the complete palette in compact RGB triplets.
- `xnto32()` expands small bitfields to 32-bit intensity, and `setcolour()` converts 32-bit intensities to 6-bit VGA DAC values.

Important details:
- Palette indexes are XORed with `0xFF` when initialized, matching Plan 9’s historic colormap expectations.
- VGA DAC values are 6-bit, even when higher-level color calculations use 32-bit intermediate values.

Filesystem relevance:
- Indirect: part of display mode setup, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/palette.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.c

Provides raw PCI configuration-space scanning and access helpers for `aux/vga`.

Key behavior:
- Detects PCI configuration mechanism 2 first, then mechanism 1, and records max device number accordingly.
- `pciscan()` walks bus/device/function space, creates `Pcidev` records, captures vendor/device/revision/class/interrupt data, and probes BAR sizes for common device classes.
- Recursively discovers PCI-PCI bridges, initializing secondary/subordinate bus numbers when firmware did not.
- Provides 8-, 16-, and 32-bit read/write helpers over both PCI config mechanisms.
- `pcimatch()` iterates the global flat PCI list by vendor/device.
- `pcihinv()` prints a hierarchical PCI inventory with class, IDs, interrupt line, and BAR data.

Important details:
- The file explicitly notes this is unsafe without locks or restrictions on what can be poked.
- BAR probing temporarily writes all ones to device registers and restores the original value.
- Bridge scanning may modify command/status and bus-number registers.
- Global state is lazily initialized and not concurrency-safe.

Filesystem relevance:
- Indirect: display drivers use this to find PCI video adapters and MMIO apertures before configuring Plan 9’s video device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.h

Defines PCI bus encodings, PCI configuration register offsets, and the `Pcidev` structure used by `aux/vga`.

Key contents:
- Bus type enum values, including `BusPCI`.
- `MKBUS`, `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and `BUSUNKNOWN` macros for Plan 9 TBDF encoding.
- Type 0/type 1 PCI configuration offsets for IDs, command/status, class codes, header type, BARs, interrupt fields, bridge bus numbers, memory/I/O windows, and bridge control.
- `Pcidev` fields for TBDF, vendor/device/revision IDs, six BAR records, interrupt line, class/subclass, flat list link, bridge child link, and same-bus link.

Important details:
- BAR records store both original BAR value and probed size.
- The same struct supports both the recursive bus tree and global flat matching list.

Filesystem relevance:
- Indirect: shared hardware-discovery definitions for VGA controllers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.c

Implements a Radeon `aux/vga` backend for selected ATI Radeon 7000/7200/7500/8500/9000/9500/9700-era adapters.

Key behavior:
- Defines `Radeon` state for MMIO, PCI device, BIOS data, framebuffer size, display type, common display registers, CRTC timing, PLL programming, and R300 workaround state.
- Provides MMIO and PLL access helpers: `OUTREG`, `INREG`, `OUTREGP`, `OUTPLL`, `INPLL`, and `OUTPLLP`.
- `radeon_getbiosparams()` reads ATI BIOS tables from `0xC0000` or `0xE0000` and extracts reference clock, divider, PLL min/max, and xclk.
- `radeonpci()` matches ATI PCI devices against `radeon_pciids` from `radeon.h`.
- `snarf()` disables generic VGA loading, attaches `radeonmmio`, reads framebuffer size, rejects non-CRT display paths, and captures bus/PLL state.
- `init()` initializes common registers, CRTC timings, pitch, DAC mode, and PLL values from the selected mode.
- `load()` blanks output, writes common/CRTC/PLL registers, unblanks, and initializes a grayscale palette ramp for true-color depths.

Important details:
- Flat-panel and LCD outputs are detected but rejected.
- PLL frequency input is scaled to BIOS-style units by `mode->frequency / 10000`.
- R300 chips need an additional PLL read workaround after indexed PLL access.
- `dump()` is effectively a stub.
- This backend relies heavily on register constants and PCI ID tables in `radeon.h`.

Filesystem relevance:
- Uses `#v/vgactl` and `segattach("radeonmmio")`; it configures Plan 9 video devices through the device namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.h

Provides Radeon register definitions, bit masks, BIOS helpers, command processor constants, and supported ATI PCI IDs for `radeon.c`.

Key contents:
- `BIOS8`, `BIOS16`, and `BIOS32` macros plus `BIOS_START`.
- Register offsets and masks for PCI config, AGP, VGA compatibility, BIOS scratch, bus control, memory configuration, CRTC/CRTC2, DAC, cursor, flat-panel/LVDS, GPIO/DDC, overlay/video scaler, palette, PLL, surface, interrupt, and wait/flush control.
- 2D engine constants for brush, destination/source coordinates, pitches, Bresenham line state, ROP3, clipping, host data, and GUI master control.
- 3D/TCL constants for pixel pipeline, texture formats/blends, cube maps, render backend, stencil/depth, setup engine, viewport, lighting, matrices, vertex formats, and material/light state.
- Command processor and microcode registers, CP packet type definitions, packet-3 opcodes, vertex control format masks, and shader/light address constants.
- `ATI_PCIVID`, `struct pciids`, Radeon family enum values, and `radeon_pciids[]` mapping device IDs to R100/R200/R300/mobile families.

Important details:
- Header comments warn it was converted from `r128_reg.h` and contains unaudited definitions that may be incorrect for Radeon.
- The R300 `R300_PPLL_REF_DIV_ACC_MASK` macro uses `(0x3ff < 18)`, which reads as a suspicious comparison rather than a shift.
- Many constants are unused by `radeon.c` but likely copied for future acceleration or broader driver use.
- The PCI ID table terminates with a zero `did`.

Filesystem relevance:
- Indirect: register definition support for the Radeon video backend, not filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/radeon.h -->