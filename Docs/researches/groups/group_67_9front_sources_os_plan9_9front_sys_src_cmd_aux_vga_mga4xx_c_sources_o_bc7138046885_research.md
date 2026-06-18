# Group Research: group_67_9front_sources_os_plan9_9front_sys_src_cmd_aux_vga_mga4xx_c_sources_o_bc7138046885

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga4xx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga4xx.c

Plan 9 `aux/vga` controller module for Matrox MGA G200/G400/G450/G550 adapters. It implements PCI discovery, MMIO/framebuffer segment attachment, VRAM probing, Matrox CRTC/DAC/sequencer register calculation, pixel PLL programming, mode loading, palette setup, and controller descriptors for `mga4xx` plus a mostly-dump-only `mga4xxhwgc`.

Key behavior:
- Defines register offsets and bit fields for Matrox PCI config registers, control aperture VGA-compatible registers, CRTC extension registers, RAMDAC indexes, pixel PLLs, and mode-control bits.
- Uses an `Mga` private state object to store PCI identity, mapped MMIO/framebuffer pointers, probed framebuffer size, PLL fields, PCI option registers, computed VGA/Matrox register images, timing fields, and aperture size.
- `snarf` finds Matrox PCI device IDs `MGA4XX`, `MGA550`, or `MGA200`, verifies memory-space enablement, maps `mga4xxmmio` and `mga4xxscreen`, enters MGA mode, and probes VRAM in 2 MiB steps by write/read tests through the framebuffer.
- `init` validates depth and non-interlace constraints, computes timing fields from `Mode`, computes pixel PLL settings for G200/G400 or stores requested frequency for G450/G550, builds VGA CRTC and CRTC-extension register images, initializes sequencer/graphics/attribute images, and disables generic `vga*` load hooks because this driver needs a custom order.
- `load` writes sequencer, attribute, graphics, DAC, PLL, CRTC, and CRTC-extension state in a hardware-specific sequence: video off, cursor off, PLL programming, DAC mode selection for 8/16/24/32 bpp, CRTC load, MGA mode enable, framebuffer endian setup for 24/32 bpp, mapping enable, screen enable, palette initialization, and cursor restore.
- G450/G550 PLL code builds and sorts candidate M/N/P values, tests lock stability around candidate offsets, and writes the best usable MNP triplet.

Notable dependencies:
- Plan 9 VGA framework types and helpers from `vga.h`, including `Vga`, `Ctlr`, `Mode`, `trace`, `vgactlpci`, `vgactlw`, `resyncinit`, and shared controller linkage.
- PCI helpers from `pci.c`/`pci.h`: `pcimatch`, `pcicfgr8`, `pcicfgr32`.
- Plan 9 segment attachment for hardware mappings via `segattach`.

Research notes:
- This is low-level display hardware initialization code, not filesystem code, but it is in the subset A 9front tree.
- Several hardware waits are unbounded busy loops, especially PLL-lock waits. A non-locking or wedged device could hang the utility.
- The VRAM probe writes test bytes into framebuffer memory. It restores only the CRTC extension mode bit, not previous framebuffer contents at tested offsets.
- `options` aligns `vga->virtx` to 128 pixels, which affects pitch and mode memory layout.
- `setpalettedepth` accepts 16 but is called only for 8 bpp in this file.
- The code uses many constants and comments adapted from old XFree86/Matrox references; behavior is tightly coupled to early-2000s hardware assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga4xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/neomagic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/neomagic.c

Plan 9 `aux/vga` controller module for NeoMagic MagicGraph/MagicMedia laptop graphics adapters. The file describes itself as a fake driver: it wraps generic VGA setup, adds NeoMagic-specific extended CRT/graphics register save/load, derives LCD panel parameters, enables linear/MMIO behavior, and supports 8/16/24 bpp modes.

Key behavior:
- Defines a small `Neomagic` private object holding the matched PCI device and detected panel dimensions.
- `snarf` calls `generic.snarf`, unlocks NeoMagic graphics registers, reads selected extended CRTC and graphics registers into `vga`, matches vendor `0x10C8`, and sets memory size, aperture size, and maximum clock by device ID.
- Supported device IDs include MagicGraph 128 ZV/ZV+, MagicGraph 128 XD, MagicMedia 256 AV/ZX/XL+. Older MagicGraph 128 variants error out as unsupported.
- `options` advertises and enables linear framebuffer support through `Ulinear|Hlinear`.
- `init` calls `generic.init`, infers panel size from graphics register bits, configures LCD-only panel output, optional centering for modes smaller than the panel, extended CRTC offset, system interface control, color mode extension, pitch, palette entries for 16/24 bpp, and forces nonstandard pixel clocks through `vga->misc |= 0x0C`.
- `load` writes key NeoMagic graphics registers around `generic.load`, enables MMIO/linear state, writes panel centering/control registers, and invokes `palette.load` for non-8-bpp modes.
- `dump` prints generic VGA state plus NeoMagic extended CRTC and graphics register ranges.

Notable dependencies:
- Shared `generic` and `palette` controllers from the VGA framework.
- PCI enumeration via `pcimatch`.
- VGA indexed register helpers `vgaxi`, `vgaxo`, direct port I/O, and Plan 9 `sleep`.

Research notes:
- There is a likely switch fallthrough bug in `init`: panel-detection case `2` sets 1024x768 but lacks a `break`, so it falls into case `3` and overwrites the panel as 1280x1024.
- The condition `if(0 && (nm->pci->did == 0x0005) || (nm->pci->did == 0x0006))` effectively selects only DID `0x0006`, because the first half is always false.
- The file exposes `neomagichwgc` as a no-op controller descriptor; hardware cursor implementation is not present here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/neomagic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/nvidia.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/nvidia.c

Plan 9 `aux/vga` controller for older NVIDIA/Riva/GeForce adapters. It detects NVIDIA PCI graphics devices, maps MMIO, classifies architecture generation, computes pixel PLL values, programs VGA CRTC extension registers, handles selected laptop/flat-panel state, initializes framebuffer memory limits, and seeds PFIFO/PGRAPH/PRAMIN acceleration objects.

Key behavior:
- `Nvidia` private state stores PCI identity, architecture class, crystal frequency, MMIO block pointers (`pfb`, `pramdac`, `pmc`, `ptimer`, `pfifo`, `pramin`, `pgraph`, `fifo`, `pcrtc`), saved CRTC extension registers, PLL fields, flat-panel fields, and head/dual-head flags.
- `snarf` chooses a PCI device from `vga->pci` or by matching NVIDIA vendor `0x10DE` and display class, maps `nvidiammio`, assigns sub-block pointers, resolves special PCI-X device IDs, classifies NV architecture 4/10/20/30/40 from device ID ranges, unlocks CRTC extensions, determines crystal frequency, dual-head and two-stage-PLL support, laptop LCD IDs, framebuffer size, saved VGA/NVIDIA registers, flat-panel dimensions, and controller state.
- `clock` searches valid M/N/P pixel PLL values based on crystal frequency, architecture, and one-stage versus two-stage PLL rules.
- `init` rejects 24-bit color, optionally forces LCD from mode attributes, computes cursor memory placement, VPLL/general state, blanking/overscan adjustments, overflow bits, pixel-depth fields, LCD scale bits, dual-head ownership, dither bits, and display height fields.
- `load` unlocks the chip, initializes PMC/PTIMER, writes memory-region registers, fills PRAMIN object tables for NV4x or older layouts, initializes PGRAPH based on architecture and device family, initializes PFIFO, writes head/cursor/LCD registers, writes CRTC extension registers, programs PLLs for CRT output or scale/sync registers for LCD output, and enables CRTC.
- `dump` reports computed PLL frequency and important NVIDIA state fields.

Notable dependencies:
- Plan 9 PCI helpers and VGA register helpers.
- `segattach` mapping named `nvidiammio`.
- Hardware constants are embedded directly in the source; this file does not include `riva_tbl.h` even though that header contains related NVIDIA initialization tables.

Research notes:
- The implementation covers a broad but old set of NVIDIA chips through hard-coded register offsets and device ID cases.
- Several register writes use array indexes that are already word-scaled in some blocks and byte-offset-divided in others; this is intentional in context but makes maintenance error-prone.
- If nForce special host-bridge lookup fails, `pcicfgr32(p, ...)` can be reached with `p == nil`.
- LCD support is partial and policy-heavy: many laptop IDs force `islcd`, and a mode attribute can override it.
- `nvidiahwgc` is a no-op descriptor; cursor setup lives inside the main mode-load path rather than a separate hardware-cursor controller.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/nvidia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/palette.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/palette.c

Generic VGA DAC palette controller for Plan 9 `aux/vga`. It reads, initializes, loads, and dumps the 256-entry VGA palette and pixel mask.

Key behavior:
- `xnto32` expands an `n`-bit color component into a 32-bit repeated pattern for scaling.
- `setcolour` stores high 6-bit red/green/blue values into a DAC palette entry.
- `snarf` reads the current pixel mask, status, and all `Pcolours` DAC entries through VGA palette ports.
- `init` clears the palette, sets pixel mask to `0xFF`, and builds either an 8-bit indexed color cube with special gray entries or a 16-entry grayscale ramp for other depths.
- `load` writes the pixel mask and all DAC entries back to hardware.
- `dump` prints palette values in compact rows.

Notable dependencies:
- VGA port helpers `vgai`/`vgao`, palette constants `Pcolours`, `PaddrR`, `PaddrW`, `Pdata`, `Pixmask`, and color indexes from `vga.h`.

Research notes:
- Palette indexes are XORed with `0xFF` during initialization, matching Plan 9’s expected color map ordering.
- DAC values are 6-bit components even though inputs are represented through 32-bit expansion helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/palette.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.c

Small Plan 9 PCI enumeration and config-space access layer used by VGA controller modules.

Key behavior:
- Maintains global linked list `pcilist`/`pcitail` of `Pcidev` objects discovered from Plan 9 PCI device files.
- `pcicfginit` opens `/dev/pci` or fallback `#$/pci`, scans directory entries whose names contain `ctl`, parses bus/device/function from file names, opens each raw config file, reads the control file, parses class/vendor/device/interrupt and BAR/size records, reads revision ID from config space, and appends the device to the list.
- `pcicfgrw` performs little-endian pread/pwrite config-space transactions of length 1, 2, or 4 through the `rawfd`.
- Exports `pcicfgr8/16/32`, `pcicfgw8/16/32`, and `pcimatch`.
- `pcimatch` lazily initializes the device list and then returns the next matching vendor/device entry after `prev`, treating DID `0` as wildcard.

Notable dependencies:
- Plan 9 `/dev/pci` or `#$/pci` device file interface.
- Endian helpers `GBIT8/16/32` and `PBIT8/16/32`.
- `Pcidev` structure and constants from `pci.h`.

Research notes:
- Allocated `Dir *d` from `dirreadall` is not freed in this file; for a short-lived VGA setup utility this is low impact.
- Parsing assumes current Plan 9 PCI ctl formatting and fixed offsets into the read buffer for class/vendor/device fields.
- `strstr(d[i].name, "ctl")` is broad but works for the expected PCI control-file naming scheme.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.h

Header defining the lightweight PCI abstraction used by the VGA utility.

Key contents:
- Bus type enumeration, including ISA, EISA, MCA, PCI, PCMCIA, NuBus, VLB, VME, and other legacy bus classes.
- `MKBUS` and `BUS*` macros for packing and extracting type/bus/device/function into a TBDF integer.
- PCI config-space register offsets for common header fields, type 0 device BAR/subsystem/ROM fields, and type 1 bridge bus/window fields.
- `Pcidev` structure containing TBDF, vendor/device/revision IDs, six memory BAR descriptors with base and size, interrupt line, class fields, linked-list pointer, and raw config FD.
- Declaration for `vgactlpci(Pcidev *)`.

Notable dependencies:
- Assumes Plan 9 integer typedefs such as `ushort`, `uchar`, `uvlong`, and `vlong`.

Research notes:
- This is a local utility header, not a complete PCI subsystem API.
- Only the fields needed by VGA hardware setup are represented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/pci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.c

Plan 9 `aux/vga` controller for ATI Radeon R100/R200/R300-era cards. It maps Radeon MMIO, reads BIOS PLL parameters, computes CRTC timing and pixel PLL registers, programs CRT output, and initializes palette/gamma for true-color modes.

Key behavior:
- `Radeon` private state stores MMIO base, PCI device, BIOS bytes, framebuffer size, display type, saved/common registers, CRTC timing registers, PLL limits and computed PLL values, and an R300 PLL-read workaround flag.
- Low-level helpers `OUTREG8`, `OUTREG`, `INREG`, `OUTREGP`, `OUTPLL`, `INPLL`, and `OUTPLLP` abstract MMIO and indexed PLL access.
- `radeon_getbiosparams` reads a video BIOS from `0xC0000` or `0xE0000`, validates the `0x55 0xAA` signature, and extracts reference frequency, reference divider, min/max PLL frequency, and xclk from the BIOS PLL info block.
- `radeonpci` matches ATI vendor `0x1002` against `radeon_pciids` from `radeon.h` and reports whether the device is R300.
- `snarf` disables generic VGA load hooks, maps `radeonmmio` from PCI BAR 2, reads framebuffer size, rejects non-CRT display output, reads BIOS parameters, and saves bus control.
- `radeon_init_common_registers`, `radeon_init_crtc_registers`, and `radeon_init_pll_registers` derive common disable/default state, CRTC format/timing/pitch state, and PLL reference/feedback/post-div values from the requested `Mode`.
- `load` blanks display, writes common registers, writes CRTC timing registers, performs atomic PPLL update, unblanks, and initializes a grayscale palette for modes above 8 bpp.

Notable dependencies:
- Register constants and PCI ID table from `radeon.h`.
- `readbios` from `io.c`.
- Plan 9 PCI/VGA framework functions `pcimatch`, `vgactlpci`, `vgactlw`, `segattach`, controller flags, and mode structures.

Research notes:
- Only CRT output is supported; flat panel/TMDS detection causes an error.
- BIOS parsing does not guard all failure modes beyond signature checks; if `readbios` fails unexpectedly, dereferences would be unsafe.
- PLL units are handled in 10 kHz units when `mode->frequency / 10000` is passed into `radeon_init_pll_registers`, matching the BIOS-style PLL fields.
- R300 PLL reads require a workaround read sequence after `INPLL`.
- `dump` is effectively a stub.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.h

Large Radeon register-definition header used by `radeon.c`. It is adapted from ATI/XFree86-era Radeon/Rage128 material and contains MMIO offsets, PLL offsets, bit masks, packet constants, and supported PCI IDs.

Key contents:
- Copyright/license notice and a warning that the file was converted from `r128_reg.h` and may contain definitions not correct for Radeon without a full audit.
- BIOS access macros `BIOS8`, `BIOS16`, `BIOS32` and `BIOS_START`.
- Register offsets and bit fields for PCI config aliases, AGP, VGA attribute/graphics/sequence registers, BIOS scratch registers, brush/2D engine registers, bus control, clock/PLL access, color compare, CRTC1/CRTC2 timing and cursor registers, DAC registers, GPIO/DDC, overlays, flat-panel/LVDS/TMDS controls, memory controller, RBBM/reset/status, 2D destination cache, scissor/source/destination registers, surface registers, wait/idle controls, 3D/texture/render backend/TCL registers, command processor registers, and CP packet formats.
- Constants for AGP texture offset, scratch registers, CP packet type construction, vertex format/control fields, and shader/light/material address slots.
- ATI vendor ID, `struct pciids`, Radeon family enum values, and `radeon_pciids[]` entries for Mobility M7/M9, RV100/R100/R200/RV200/RV250, and R300 device IDs.

Notable dependencies:
- Intended to be included in C files that already define Plan 9 types such as `uchar`, `ushort`, and `ulong`.
- `struct pciids` and `radeon_pciids[]` are concrete definitions, so this header should not be included by multiple translation units without care.

Research notes:
- Many definitions are unused by the local `radeon.c`, which uses mainly BIOS macros, CRTC/DAC/PLL/common register constants, and PCI ID data.
- There is a suspicious mask definition: `R300_PPLL_REF_DIV_ACC_MASK` is written as `(0x3ff < 18)` rather than a left shift. That expression evaluates as a comparison, not the intended bit mask, and affects R300 PLL handling in `radeon.c`.
- Because this is a direct hardware-definition header with embedded data, validation risk is about register correctness rather than control flow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/radeon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524.c

Plan 9 VGA RAMDAC/clock controller for IBM RGB524 DACs attached to S3 Vision96x-style adapters.

Key behavior:
- Defines RGB524 index/data access constants and index-register numbers for pixel format, PLL control/reference/frequency registers, misc clock/control registers, and DAC control fields.
- `setrs2` temporarily changes S3 CRTC register `0x55` to route DAC extended register access, while `restorers2` restores it.
- `rgb524xi`/`rgb524xo` read and write RGB524 indexed registers through `dacxreg`.
- `clock` selects direct RGB524 frequency-byte encoding for requested pixel clock ranges from about 16.25 MHz through 220 MHz.
- `init` parses optional speed grade from controller name, validates requested pixel clock, optionally enables clock-doubling for 8 bpp, chooses standard VGA clock selection or programmed PLL selection, and sets controller init state.
- `load` sets known VGA frequencies, optionally programs a `rgb524refclk` attribute, enables pixel programming and clock doubling, sets pixel format for 1/8 bpp, updates misc controls, programs direct frequency register `Frequency0+3` when using PLL selection 3, and mirrors clock selection into CRTC register `0x22`.
- `dump` prints many DAC index ranges and decodes reference and direct-clock frequency entries.

Notable dependencies:
- S3 CRTC register helpers and external `dacxreg` access table from the VGA framework.
- Mode attributes via `dbattr`.

Research notes:
- This file assumes a specific S3-to-RGB524 wiring and is not a general RGB524 driver.
- It supports only 1 bpp and 8 bpp pixel-format programming in `load`.
- PLL wait/lock handling is minimal compared with newer DAC drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524mn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524mn.c

Generic IBM RGB52x-compatible RAMDAC controller using externally supplied indexed register access functions. It computes M/N/divider PLL settings and programs pixel-format, sync, and clock registers for 8/15/16/32 bpp modes.

Key behavior:
- Exports global function pointers `rgb524mnxi` and `rgb524mnxo`; another chip-specific controller must install these to read/write DAC registers.
- Defines RGB52x index registers for misc clock, sync control, pixel controls, PLL controls, SYSCLK, M/N clock pairs, and misc controls.
- `clock` brute-forces divider, M, and N values against the reference clock and max pixel clock, choosing the closest output frequency while respecting VCO/reference constraints.
- `init` parses speed grade from the controller name, uses `rgb524mnrefclk` or default `RefFreq`, validates requested pixel clock, computes PLL values, and selects M/N pair 2.
- `load` verifies callbacks exist, writes selected M/N registers and PLL controls, enables pixel programming and internal PLL clock, sets sync polarity, chooses hsync delay by mode depth or `hsyncdelay` attribute, programs SYSCLK constants, and writes pixel-format/pixel-control registers by depth.
- `dump` reads register ranges and decodes SYSCLK and active pixel PLL frequency.

Notable dependencies:
- External DAC access callbacks must be provided before `load`/`dump`.
- Uses VGA mode and attribute metadata from `vga.h`.

Research notes:
- There is a likely bug in the 15-bpp switch case: after setting `Pixel16Control` to `0xC4`, it falls through into the 16-bpp case and overwrites it with `0xC6`.
- The hard-coded SYSCLK writes and sleeps are visible in `load`, including commented-out alternate values, indicating empirically tuned hardware setup.
- The comment says palette setup needs work for modes other than 8 bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/rgb524mn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/riva_tbl.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/riva_tbl.h

NVIDIA RIVA fixed-function initialization table header derived from old NVIDIA/XFree86 sources. It contains static address/value tables for initializing PMC, PTIMER, FIFO/PFIFO, PGRAPH, and PRAMIN state across NV3, NV4, and NV10 generations, including depth-specific table variants.

Key contents:
- Common `RivaTablePMC`, `RivaTablePTIMER`, and `RivaTableFIFO` tables.
- NV3 tables for PFIFO, PGRAPH, PGRAPH depth variants for 8/15/32 bpp, PRAMIN, and PRAMIN depth variants.
- NV4 tables for FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, PRAMIN, and PRAMIN depth variants.
- NV10 tables for FIFO, PFIFO, PGRAPH, PGRAPH depth variants, an additional `nv10tri05TablePGRAPH` table with many 3D state/register values, PRAMIN, and PRAMIN depth variants.
- Tables are simple `static unsigned[][2]` pairs, with first element being an offset/index and second element being the value to write.

Notable dependencies:
- No includes or helper macros; consumers are expected to know the target MMIO block and whether table offsets are byte offsets or already word-scaled.

Research notes:
- The header is not included by `nvidia.c` in this directory; that driver contains its own imperative initialization sequence instead.
- Because all symbols are `static`, inclusion in one or more C files would create translation-unit-local copies.
- It is data-only, so correctness depends on pairing the right table with the right architecture and color depth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/riva_tbl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3801.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3801.c

Plan 9 `aux/vga` controller wrapper for S3 86C801/86C805 GUI accelerators.

Key behavior:
- Delegates `snarf`, most initialization, loading, and dumping to `s3generic`.
- `options` advertises enhanced-mode capability with `Henhanced`.
- `init` calls `s3generic.init`, adjusts CRTC register `0x3B`, rejects depths above 8 bpp, sets display-memory access registers `0x60` through `0x62`, and chooses guessed `Crt54` values based on horizontal resolution.
- `load` calls `s3generic.load`, writes registers `0x60` through `0x62`, and sets S3 advanced function control port `0x4AE8` when enhanced mode is active.
- Exports two descriptors, `s3801` and `s3805`, with identical behavior.

Notable dependencies:
- Shared `s3generic` controller and VGA register/port helpers.

Research notes:
- Comments explicitly describe some timing/memory parameters as guesses based on register dumps.
- Depth support is limited to 1/8 bpp class modes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3801.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3928.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3928.c

Plan 9 `aux/vga` controller wrapper for the S3 86C928 GUI accelerator.

Key behavior:
- Delegates base behavior to `s3generic`.
- `options` advertises linear aperture and enhanced-mode support.
- `init` pre-validates depth before generic overflow calculations, optionally reinitializes timing for enhanced 8-bpp modes at 1024 pixels or wider, calls `s3generic.init`, adjusts `Crt3B`, sets write posting/read-ahead cache controls, and configures parallel VRAM, external SID, and E-step bug workaround bits depending on RAMDAC flags and enhanced mode.
- `load` calls `s3generic.load`, writes `Crt65`, and sets the advanced function control word at port `0x4AE8`.
- `dump` delegates to `s3generic.dump`.

Notable dependencies:
- `s3generic`, `resyncinit`, RAMDAC flags such as `Hpvram` and `Hextsid`, and direct port output.

Research notes:
- Depths above 8 bpp are rejected.
- The file has special early timing setup because generic overflow calculation depends on final CRTC values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3928.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3clock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3clock.c

S3-specific clock loading helper controller for programmable clocks that require S3 CRTC/Misc register sequencing.

Key behavior:
- `setcrt42` safely changes S3 CRTC register `0x42` clock-select bits by temporarily manipulating VGA Misc and sequencer state.
- `icd2061aload` serializes a 24-bit ICD2061A clock word using CRTC register `0x42` data/clock bits, including unlock, start, modified Manchester data, stop, and final clock selection. It repeats loading three times from the generic `load` dispatcher.
- `ch9294load` selects a Chrontel 9294-style clock through CRTC `0x42`.
- `tvp3025load` and `tvp3026load` program TI TVP3025/3026 RAMDAC clock registers through DAC-specific helpers, with special paths for 1-bpp standard clocks and 8-bpp programmed clocks.
- `init` validates that `vga->clock->name` matches a known clock prefix, initializes the underlying clock controller if necessary, supplies default pixel clock from the mode, and adjusts `vga->misc` for nonstandard clocks.
- `load` dispatches to the matching clock loader and marks the controller loaded.

Notable dependencies:
- External DAC helpers `tvp3020xo`, `tvp3026xo`, `tvp3026xi`.
- Existing `vga->clock` controller fields for M/N/P/D/I/Q clock parameters.
- Direct VGA port I/O.

Research notes:
- Busy waits for TVP3026 PLL lock are unbounded.
- Clock name matching strips a suffix after `-`, allowing speed-grade or variant suffixes.
- The controller is only meaningful when paired with a concrete clock/RAMDAC controller that has already computed PLL fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3generic.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3generic.c

Generic S3 GUI accelerator support used by multiple S3 chip-specific controllers. It unlocks and captures S3 extended CRTC registers, computes generic enhanced/linear-aperture state, loads common S3 registers, and dumps/decodes timing values.

Key behavior:
- `snarf` unlocks S3 extended registers with CRTC `0x38/0x39`, reads registers `0x30` through `0x6F`, and derives framebuffer size from CRTC `0x36`.
- `init` decides whether enhanced mode is necessary/usable, rejects unsupported wide 1-bpp modes, sets common S3 extended register values, handles interlace bits, chooses horizontal display size code in `Crt50`, configures a placeholder linear aperture, computes aperture size and `Ulinear` state, and packs high overflow bits into `Crt5D`/`Crt5E`.
- `load` writes common extended registers, programs linear aperture base/size when `Ulinear` is active, and marks the controller loaded.
- `dump` prints extended CRTC ranges and, when not dumping initialized state, decodes horizontal and vertical timing values from S3 overflow registers, including special scaling heuristics for 928/Vision964 and ViRGE variants.

Notable dependencies:
- S3 chip-specific wrappers such as `s3801.c` and `s3928.c`.
- VGA framework helpers `resyncinit`, `vgaxi`, `vgaxo`, `printitem`, and `printreg`.

Research notes:
- The generic controller sets `ctlr->type = s3generic.name`, so chip-specific drivers can share a common type marker.
- Linear aperture setup initially assumes a 64 KiB aperture at VGA memory, then final base/size is resolved before load from `vga->vmb`/`vga->vmz`.
- Timing decode in `dump` is heuristic and partly chip-name-dependent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3hwgc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3hwgc.c

Hardware graphics cursor gatekeeping descriptors for S3/RAMDAC combinations.

Key behavior:
- `init` marks the controller initialized, returns immediately if global `cflag` is already set, and otherwise requires an active VGA controller with enhanced-mode capability and depth at least 8. If requirements are not met, it disables cursor use via `cflag`; if they are met, it requests enhanced mode through `resyncinit`.
- `load` marks loaded and verifies enhanced mode is actually active at load time, disabling cursor use through `cflag` if not.
- Exposes no-op descriptors for `bt485hwgc`, `rgb524hwgc`, `tvp3020hwgc`, and `tvp3026hwgc`.
- Exposes `s3hwgc` with the active `init`/`load` validation logic.

Notable dependencies:
- Global cursor-disable flag `cflag`, current controller `vga->ctlr`, enhanced-mode flags, and `resyncinit` from the VGA framework.

Research notes:
- This file does not program cursor shape, colors, or position; it only enforces prerequisites and provides controller names for configuration.
- The no-op descriptors likely let configuration files name RAMDAC-specific cursor controllers while actual cursor support is elsewhere or absent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3hwgc.c -->