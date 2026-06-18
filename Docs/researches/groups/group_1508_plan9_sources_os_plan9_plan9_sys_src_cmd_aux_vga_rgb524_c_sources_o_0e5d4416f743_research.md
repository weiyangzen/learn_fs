# Group Research: group_1508_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_vga_rgb524_c_sources_o_0e5d4416f743

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524.c

IBM RGB524 RAMDAC support for Plan 9 `aux/vga`, assuming attachment to S3 Vision964/968-style hardware.

Key behavior:
- Accesses RGB524 indexed registers through DAC index/data ports after temporarily setting S3 CRTC register `0x55` RS2 routing.
- Validates requested pixel clock against controller name speed suffix, defaulting to 170 MHz.
- Chooses VGA fixed clocks when possible, otherwise programs RGB524 direct frequency registers.
- Supports optional `rgb524refclk` database attribute and optional 8-bit clock doubler path through `Uclk2`.
- Sets pixel format for 1 bpp and 8 bpp modes, MiscClock/MiscControl registers, and S3 `Crt22` when using programmed PLL clock.
- Dumps register banks and decodes direct programmed frequencies.

Integration:
- Exports `Ctlr rgb524`.
- Uses shared `Vga` clock fields `f/d/i` and controller flags `Finit`, `Fload`, `Uclk2`.
- Filesystem relevance is indirect: hardware configuration utility code, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524mn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524mn.c

Generic IBM RGB52x/RGB524-compatible RAMDAC module using caller-supplied indexed-register access callbacks.

Key behavior:
- Exports global function pointers `rgb524mnxi` and `rgb524mnxo`; board code such as `t2r4.c` installs accessors.
- Brute-force searches divider/select values for the closest pixel clock under reference-clock and max-pixel-clock constraints.
- Uses `rgb524mnrefclk` database attribute or `RefFreq`.
- Programs M/N register pair 2 by default and selects internal PLL frequency.
- Configures SyncControl polarity, HSync delay, SYSCLK registers, palette control, and pixel format/control for 8, 15/16, and 32 bpp modes.
- Dumps register banks plus SYSCLK and selected pixel PLL clocks.

Important details:
- `load()` errors if access callbacks are unset.
- 15 bpp case falls through into 16 bpp setup after writing `0xC4`, likely intentional or unfinished given the comment about non-8-bit work.
- Contains hard-coded SYSCLK programming and sleeps.

Filesystem relevance:
- Indirect hardware-support code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/rgb524mn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/riva_tbl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/riva_tbl.h

Static NVIDIA RIVA initialization table header, copied from NVIDIA/XFree86-era sources.

Contents:
- Copyright/license notice from NVIDIA and XFree86 revision marker.
- Common fixed-function tables:
  - `RivaTablePMC`
  - `RivaTablePTIMER`
  - `RivaTableFIFO`
- NV3 tables:
  - PFIFO, PGRAPH, PGRAPH depth variants for 8/15/32 bpp, PRAMIN, PRAMIN depth variants.
- NV4 tables:
  - FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, PRAMIN, PRAMIN depth variants.
- NV10 tables:
  - FIFO, PFIFO, PGRAPH, PGRAPH depth variants for 8/15/16/32 bpp, `nv10tri05TablePGRAPH`, PRAMIN, PRAMIN depth variants.

Behavior:
- No functions or control flow.
- Provides register/value pairs consumed by NVIDIA/RIVA driver code elsewhere.
- Depth-specific tables adjust graphics object and PRAMIN format state for color layout.

Filesystem relevance:
- Indirect: static display hardware initialization data, not storage code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/riva_tbl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3801.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3801.c

S3 86C801/86C805 GUI accelerator support.

Key behavior:
- Delegates snarf/init/load/dump baseline work to `s3generic`.
- Advertises enhanced mode capability.
- Rejects depths above 8 bpp.
- Sets S3 display FIFO/start and memory access control registers `Crt3B`, `Crt54`, `Crt60-62`.
- Writes advanced-function control port `0x4AE8`, selecting enhanced values for common 800/1024 widths.

Integration:
- Exports `Ctlr s3801` and `Ctlr s3805` with identical routines.
- Filesystem relevance is indirect display-configuration support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3801.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3928.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3928.c

S3 86C928 GUI accelerator support.

Key behavior:
- Advertises linear framebuffer and enhanced mode.
- Rejects depths above 8 bpp.
- For enhanced 8 bpp modes at 1024+ width, recalculates horizontal CRTC timing in quarter-pixel units before calling `s3generic.init()`.
- Configures FIFO/read-ahead/write-posting, parallel VRAM, external SID, and documented E-step bug workaround bits.
- Loads `Crt65` after generic load and writes advanced-function control port `0x4AE8`.

Integration:
- Exports `Ctlr s3928`.
- Uses RAMDAC flags `Hpvram` and `Hextsid` to decide controller-side options.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3928.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3clock.c

S3-specific clock loading shim for external or RAMDAC-resident clock generators.

Key behavior:
- Knows how to load:
  - `icd2061a`
  - `ch9294`
  - `tvp3025clock`
  - `tvp3026clock`
- For ICD2061A, serializes a 24-bit programming word through S3 `Crt42` using the required unlock and modified Manchester sequence.
- For CH9294, selects the S3 clock index through `Crt42`.
- For TVP3025/3026, writes RAMDAC PLL registers and associated S3 clock-select state.
- Calls the selected clock controller’s `init()` if needed and sets VGA misc clock-select bits for non-standard clocks.

Important details:
- ICD2061A load is repeated three times, matching old hardware programming folklore.
- TVP3026 load includes busy-wait loops for PLL lock bits.

Filesystem relevance:
- Indirect hardware clock programming.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3generic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3generic.c

Shared S3 SVGA/GUI accelerator support used by many controller-specific files.

Key behavior:
- Unlocks S3 extended CRTC registers and snarfs `Crt30-Crt6F`.
- Derives video memory size from `Crt36`.
- Handles enhanced-mode selection and rejects unsupported non-enhanced 1 bpp wide modes.
- Initializes S3 extended CRTC state:
  - timing overflow bits in `Crt5D/5E`,
  - interlace state,
  - display width encoding,
  - linear aperture registers,
  - mode/control registers.
- Loads extended registers in a controlled order, including optional linear aperture base/size.
- Dumps raw S3 register banks and decodes timing fields when not already initialized.

Important details:
- `ctlr->type` is set to `s3generic.name`.
- Uses `vga->virtx` for pitch-related generic VGA state.
- Dump logic special-cases ViRGE 16 bpp timing scaling.

Filesystem relevance:
- Indirect display chipset framework code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3hwgc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3hwgc.c

Hardware graphics cursor controller declarations for several RAMDAC/S3 combinations.

Key behavior:
- `s3hwgc` init/load checks whether enhanced mode and at least 8 bpp are available; otherwise sets global `cflag` to fall back away from hardware cursor.
- Requests `Uenhanced` through `resyncinit()` when possible.
- Defines placeholder cursor controllers:
  - `bt485hwgc`
  - `rgb524hwgc`
  - `tvp3020hwgc`
  - `tvp3026hwgc`

Important details:
- Placeholder RAMDAC cursor controllers have no callbacks.
- This file coordinates cursor feasibility more than actual cursor image programming.

Filesystem relevance:
- Indirect display utility code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3hwgc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/sc15025.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/sc15025.c

Sierra SC15025/SC15026 HiCOLOR-24 palette RAMDAC support.

Key behavior:
- Uses VGA DAC pixel-mask access sequencing to read/write the RAMDAC command register.
- Parses optional speed grade suffix from controller name, defaulting to 66 MHz.
- Validates requested pixel clock against the speed grade.
- Loads auxiliary indexed state through command/register access, currently with minimal 8-bit handling.
- Dumps command register and indexed registers `0x08-0x10`.

Important details:
- `options()` only marks options complete.
- Mode-specific `aux` handling is mostly disabled/commented, suggesting limited support.

Filesystem relevance:
- Indirect display hardware support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/sc15025.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/stg1702.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/stg1702.c

SGS-Thomson STG1702 enhanced true-color palette DAC support.

Key behavior:
- Implements command and indexed-register access via VGA pixel-mask sequencing.
- Advertises `Hpclk2x8` capability.
- Validates pixel clock:
  - up to 110 MHz in normal 8-bit mode,
  - up to 135 MHz when 2x8-bit mode is usable.
- If a suitable controller supports 2x8 and high 8 bpp clock is requested, halves the clock and requests `Upclk2x8`.
- Programs primary/secondary pixel mode, pipeline timing, and command register.
- Dumps command and indexed registers up to `Power`.

Filesystem relevance:
- Indirect display RAMDAC support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/stg1702.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/t2r4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/t2r4.c

Number Nine Ticket to Ride IV controller support.

Key behavior:
- Defines private `T2r4` state with PCI device, I/O base, MMIO pointer, saved I/O registers, global registers, and memory-window registers.
- Finds PCI vendor `0x105D` device `0x5348`, writes `/dev/vgactl` type `t2r4`, and attaches `t2r4mmio`.
- Saves I/O/MMIO register state, enables relevant config bits, and derives video memory/aperture size from PCI BAR.
- Installs `rgb524mn` MMIO access callbacks when the selected RAMDAC name begins with `rgb524mn`.
- Computes T2R4 display timing registers from `Mode`, including optional `zoom`.
- Configures display base, pitch, active/blank/sync widths, CRT control, and memory window 0.
- Loads MMIO global/window registers and pokes SGRAM/vgactl state with sleeps.

Integration:
- Exports `Ctlr t2r4` and placeholder `Ctlr t2r4hwgc`.
- Uses Plan 9 segment attachment and VGA control files, so it depends on kernel video-device support.

Filesystem relevance:
- Indirect; touches device namespace files like `#v/vgactl`, but purpose is display hardware setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/t2r4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/template.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/template.c

Skeleton controller template for `aux/vga` modules.

Key behavior:
- Includes no real hardware behavior.
- Defines stub `snarf`, `options`, `init`, `load`, and `dump` callbacks.
- Each stub marks the corresponding controller flag except `dump`, which only consumes arguments.
- Exports `Ctlr xxx`.

Use:
- Serves as a copy/edit template for new VGA controller modules.

Filesystem relevance:
- None beyond being source scaffolding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/template.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/trio64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/trio64.c

S3 Trio64 controller support and shared Trio/ViRGE PLL calculation helper.

Key behavior:
- Snarfs extra sequencer registers `Seq08-Seq18` plus CRTC ID registers, then delegates to `s3generic`.
- Advertises linear, 2x8 pixel clock, and enhanced mode.
- `trio64clock()` computes PLL `M/N/R` for S3 internal clock generators under part-specific limits stored in `vga->m/n/r/f[1]`.
- Rejects depths above 8 bpp.
- Uses fixed VGA clocks when possible, otherwise programs `Seq12/Seq13` PLL fields and misc clock-select bits.
- Enables internal clock generator and optional 2x8 mode.
- Configures FIFO start, memory access, VLB latch delay, and advanced function control.

Integration:
- Exports `Ctlr trio64` and function `trio64clock()` reused by `virge.c`.

Filesystem relevance:
- Indirect display hardware support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/trio64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3020.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3020.c

Texas Instruments TVP3020/3025/3026 indexed-register access and TVP3020 RAMDAC setup.

Key behavior:
- Provides exported direct/indexed register helpers:
  - `tvp3020i`
  - `tvp3020xi`
  - `tvp3020o`
  - `tvp3020xo`
- Detects chip ID through indexed register `0x3F` and validates access permissions using `directreg` and `indexreg` tables.
- Routes DAC register selection through S3 `Crt55`.
- Advertises clock doubler, external SID, parallel VRAM, and enhanced mode capability.
- Validates pixel clock against controller name speed suffix, defaulting to 110 MHz.
- Requests clock-doubled operation above 85 MHz by halving requested clock.
- Programs input/output clock selection, aux/color-key/mux controls, sync polarity, misc output sync-disable bits, and DAC GPIO selection.
- Dumps accessible direct and indexed registers.

Filesystem relevance:
- Indirect display RAMDAC support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3020.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025.c

TVP3025-specific wrapper around the TVP3020 support code.

Key behavior:
- Reuses `tvp3020.options()` and `tvp3020.init()`.
- Before loading, clears S3 `Crt5C` RS4, disables a TVP3025 bit in indexed register `0x06`, and writes register `0x0E`.
- Calls `tvp3020.load()` and, in enhanced mode, adjusts register `0x29`.
- Dumps base TVP3020 registers plus PCLK, MCLK, and RCLK PLL register sequences.
- Decodes TVP3025 clock using `RefFreq*((n+2)*8)/(d+2) >> p`.

Filesystem relevance:
- Indirect display RAMDAC support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025clock.c

TVP3025 PLL parameter calculator.

Key behavior:
- Computes `vga->d[0]`, `vga->n[0]`, and `vga->p[0]` for the desired pixel clock.
- Brute-force searches D/N/P values for:
  - `Fvco = RefFreq*((n+2)*8)/(d+2)`
  - `Fpll = Fvco / 2**p`
- Enforces approximate VCO range 110-220 MHz and reference-divider constraints.
- Sets default PLL fields before search and marks `Finit`.

Integration:
- Does not load registers itself; `s3clock.c` uses these fields in `tvp3025load()`.

Filesystem relevance:
- Indirect display clock calculation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3025clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026.c

TVP3026 RAMDAC support with distinct register access from TVP3020/3025.

Key behavior:
- Provides exported `tvp3026xi()` and `tvp3026xo()` indexed access helpers.
- Routes register access through S3 `Crt55`, using direct index register `0x00` and data register `0x0A`.
- Advertises clock doubler, external SID, and enhanced mode capability.
- Validates pixel clock against speed-grade suffix, defaulting to 110 MHz.
- Requests `Uclk2` for 8 bpp high pixel clocks above 85 MHz if not already selected.
- Load routine sets sync polarity in indexed register `0x1D`, disables VGA controller syncs through misc bits, and marks loaded.
- Dumps 16 direct registers, 64 indexed registers, and decodes PCLK/MCLK/LCLK register groups.

Important detail:
- `Ctlr tvp3026` has no `load` callback in the struct despite defining a static `load()`; setup may be delegated to `s3clock.c`/other RAMDAC paths or this is an omission.

Filesystem relevance:
- Indirect display RAMDAC support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026clock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026clock.c

TVP3026 pixel and loop clock parameter calculator.

Key behavior:
- Sets VGA misc clock-select bits for fixed VGA clocks or programmed clocks.
- Brute-force searches TVP3026 pixel PLL fields `m/n/p` for:
  - `Fvco = 8*RefFreq*(65-m)/(65-n)`
  - `Fpll = Fvco / 2**p`
- Enforces VCO range 110-250 MHz and nominal `n/m/p` constraints.
- Computes loop clock fields in `m/n/p/q[1]`, using enhanced-mode state to pick bus ratio.
- Marks `Finit`.

Integration:
- `s3clock.c` consumes these fields in `tvp3026load()`.

Filesystem relevance:
- Indirect display clock calculation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesa.c

VESA BIOS Extension and EDID support for Plan 9 `aux/vga`.

Key behavior:
- Opens `/dev/realmode` and `/dev/realmodemem`, stages BIOS call buffers at physical `0x9000`, and invokes interrupt `0x10`.
- Validates VBE 2+ signature and builds a VESA-backed `Ctlr` chain with software cursor.
- Enumerates VBE modes, queries mode info, constructs Plan 9 mode names/channels, and scans unoffered mode IDs if necessary.
- Sets VBE graphics modes using linear framebuffer and no-clear flags.
- Dumps VBE info, mode list, unoffered modes, and EDID.
- Parses EDID 128-byte blocks:
  - manufacturer/product/serial/date/version,
  - display flags,
  - established timings,
  - standard timing IDs,
  - detailed timing blocks,
  - monitor descriptor blocks for serial/name/range limits.
- Converts EDID timing data to `Mode` entries and deduplicates by generated mode name.
- Uses `vesadb.c`’s `vesamodes[]` for standard timing lookup.

Important details:
- `Vmode.chan` is derived from VBE RGB masks for direct-color modes.
- `dbvesamode()` creates a minimal Plan 9 `Mode` with attribute `id=0x...`.
- EDID parsing currently includes debug output calls (`fprint(2, "dt\n")`, hex dumps, and `print("fd ...")`).
- `vesatextmode()` switches back to mode 3 through VBE.

Filesystem relevance:
- Mostly indirect. It interacts with Plan 9 device files for real-mode BIOS access but does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesadb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesadb.c

Generated VESA DMT timing database for `vesa.c`.

Contents:
- Static `Mode` definitions for 30 standard modes:
  - 640x480 at 60/72/75/85 Hz
  - 800x600 at 56/60/72/75/85 Hz
  - 1024x768 at 60/70/75/85 Hz
  - 1152x864 at 75 Hz
  - 1280x960 at 60/85 Hz
  - 1280x1024 at 60/75/85 Hz
  - 1600x1200 at 60/65/70/75/85 Hz
  - 1792x1344 at 60/75 Hz
  - 1856x1392 at 60/75 Hz
  - 1920x1440 at 60/75 Hz
- Each mode stores active dimensions, horizontal/vertical total, blanking, sync ranges, pixel clock, sync polarity, and interlace flag.
- Exports `Mode *vesamodes[]` null-terminated lookup table.

Use:
- `vesa.c` uses it to resolve EDID established and standard timing names without relying on external `vgadb`.

Filesystem relevance:
- None directly; static display timing data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesadb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.c

Generic VGA register access and base VGA controller implementation.

Key behavior:
- Provides safe wrappers for VGA port access:
  - `vgai`
  - `vgaxi`
  - `vgao`
  - `vgaxo`
- Handles attribute-controller read/write sequencing through `Status1`.
- `snarf()` reads generic VGA misc, feature, sequencer, CRTC, graphics, attribute, and optional palette state.
- `init()` computes baseline VGA register values from `Mode`:
  - misc sync polarity and fixed clock select,
  - sequencer state,
  - CRTC horizontal and vertical timing,
  - overflow bits,
  - interlace scaling,
  - display pitch from `virtx`,
  - graphics controller state,
  - attribute controller state,
  - optional palette.
- `load()` writes generic VGA registers and optional palette.
- `dump()` prints generic VGA state plus virtual size, panning, clock fields, memory aperture/base/size, and linear flag.

Integration:
- Exports `Ctlr generic` named `vga`.
- All SVGA controller files build on this state either directly or through `s3generic`.

Filesystem relevance:
- Indirect display utility code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.h

Central header for Plan 9 `aux/vga`.

Key definitions:
- VGA I/O port constants for misc/status/feature, sequencer, CRTC, graphics, attribute, palette, pixel mask, and DAC status.
- Standard clocks `RefFreq`, `VgaFreq0`, `VgaFreq1`.
- `Ctlr`: controller module interface with `snarf`, `options`, `init`, `load`, `dump`, type, flags, and linked controller.
- Controller flags:
  - lifecycle flags `Fsnarf/Foptions/Finit/Fload/Fdump/Ferror`,
  - hardware capability/use flags for 2x8, enhanced, parallel VRAM, external SID, clock doubler/divisor, linear addressing, 32-bit SID.
- `Attr`: name/value linked-list database attributes.
- `Mode`: monitor/mode timing, channel, frequency, dimensions, sync, interlace, and attributes.
- `Vga`: full mutable VGA state, including generic registers, palette, two sets of clock fields, memory aperture/base/size, BIOS/PCI matches, mode, virtual screen, controller links, attributes, and private pointer.

Integration:
- Declares all VGA controller modules, RAMDACs, clock chips, helpers, PCI functions, database helpers, I/O helpers, and globals used across `aux/vga`.
- Documents known `virtx` vs `mode->x` pitfalls for older drivers.

Filesystem relevance:
- Indirect: display subsystem header, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/virge.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/virge.c

S3 Trio64+/ViRGE/Savage/ProSavage controller support.

Key behavior:
- Unlocks and reads extended sequencer/CRTC registers, then identifies chip variant by `Crt2D:Crt2E`.
- Handles IDs for Trio64+, Aurora64V+, Trio64V2, ViRGE, ViRGE/DX/GX, ViRGE/GX2, ViRGE/VX, Savage MX/MV, Savage4/IX, SuperSavage/IXC16, Savage4, ProSavage PN133/KN133/DDR.
- Sets PLL limits, memory sizes, and aperture sizes per chipset.
- Rounds virtual width to a multiple of 16 for Savage-family chips.
- Configures mode-specific CRTC/sequencer state for depth, byte width, FIFO, MMIO method, clocking, and color mode.
- Uses `trio64clock()` for PLL calculation, with variant-specific packing of M/N/R high bits.
- Supports `noclockset` mode attribute to avoid programming clocks.
- Loads generic S3 state, PLL registers, variant-specific registers, and advanced-function control when needed.
- Dumps extended CRTC/sequencer ranges and decodes DCLK/MCLK.

Important details:
- Comments mark some Savage/SuperSavage values as guessed or hardware-derived.
- Supports 8/15/16/24/32 bpp depending on variant; some unsupported depths error.

Filesystem relevance:
- Indirect display controller code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/virge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision864.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision864.c

S3 Vision864 controller support, similar to older 86C801/805 path.

Key behavior:
- Delegates baseline work to `s3generic`.
- Advertises linear, 2x8 pixel clock, and enhanced mode.
- Rejects depths above 8 bpp.
- Sets VLB-related bits for certain bus encodings.
- Programs display memory access registers `Crt60-62`, memory-control `Crt54`, clock-doubler mode bit in `Crt67`, and blanking/skew adjust register `Crt6D`.
- Supports database attributes `delaybl` and `delaysc`.
- Loads additional registers and writes advanced-function control port `0x4AE8`.

Filesystem relevance:
- Indirect display hardware support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision864.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision964.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision964.c

S3 Vision964 controller support.

Key behavior:
- Snarfs generic S3 state plus CRTC registers `0x22`, `0x24`, and `0x26`.
- Advertises linear and enhanced mode.
- Rejects depths above 8 bpp.
- If RAMDAC uses clock doubling, halves horizontal timings and forces enhanced mode; otherwise enhanced mode is used for 8 bpp.
- Configures external SID width/divisor based on RAMDAC flags `Hsid32` and `Uclk2`.
- Sets SAM size, display FIFO start, enhanced control bits, delay/skew attributes, and optional `sam512`.
- Loads `Crt65`, `Crt66`, `Crt6D`, and advanced-function control.

Filesystem relevance:
- Indirect display controller support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision964.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision968.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision968.c

S3 Vision968 controller support.

Key behavior:
- Snarfs generic S3 state, sequencer `0x09/0x0A`, CRTC `0x22/0x24/0x26`, and CRTC ID `0x2D-0x2F`.
- Advertises linear and enhanced mode.
- Rejects depths above 8 bpp.
- Like Vision964, handles RAMDAC clock-doubled timing by halving horizontal values and forcing enhanced mode.
- Configures SID divisor only when RAMDAC advertises external SID.
- Sets control bits for enhanced operation, SAM, display skew, optional `disa1sc`, `vclkphs`, `delaybl`, and `delaysc`.
- Special-cases non-TVP3026 RAMDAC behavior for `Crt67`.
- Loads extra registers and advanced-function control.
- Dumps S3 generic plus Vision968-specific sequencer/CRTC registers.

Filesystem relevance:
- Indirect display controller support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision968.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vmware.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vmware.c

VMware SVGA virtual video controller support.

Key behavior:
- Uses PCI device ID to select VMware register address/data ports:
  - `0x710`: fixed ports `0x4560/0x4564`.
  - `0x405`: BAR-derived ports.
- Reads VMware indexed registers into private `Vmware` state.
- Derives Plan 9 channel string from red/green/blue masks and host bits-per-pixel.
- Records framebuffer base and max size into `vga->vmb` and `vga->apz`.
- Validates SVGA version 2 by writing/reading `Rid`.
- Forces linear mode, clips requested dimensions to VMware max width/height, adopts VMware bpp, and updates `mode->chan`.
- Loads width/height, enables display, writes guest OS ID, and adjusts Plan 9 `vgactl size` if VMware bytes-per-line implies a wider virtual stride.
- Dumps all VMware registers plus channel/depth.

Integration:
- Exports `Ctlr vmware` and placeholder `Ctlr vmwarehwgc`.

Filesystem relevance:
- Indirect. It writes `/dev/vgactl` through `vgactlw()` when virtual stride changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/w30c516.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/w30c516.c

IC Works W30C516 ZOOMDAC RAMDAC support.

Key behavior:
- Defines indirect register map for control, ID, image bounds, ratio/offset, and test registers.
- Advertises `Hpclk2x8`.
- Parses speed-grade suffix, defaulting to 110 MHz; 170 MHz grade allows 135 MHz normal 8-bit pixel clock.
- If attached controller supports 2x8 and 8 bpp clock is at least 60 MHz, halves clock and requests `Upclk2x8`.
- Validates adjusted clock against allowed pclk.
- Loads by sleeping the chip, setting 2x8 mode if needed, preserving part of `Cr1`, and waking through `Cr0`.
- Dumps indirect registers via `attdaci()`.

Integration:
- Depends on ATT DAC helper functions `attdaci/attdaco`.

Filesystem relevance:
- Indirect display RAMDAC support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/w30c516.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/watchdog.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/watchdog.c

Plan 9 watchdog feeder utility.

Key behavior:
- Opens watchdog control device `#w/wdctl`.
- Forks into background using `rfork(RFPROC|RFNOWAIT|RFFDG)` and exits parent.
- Raises child process priority by writing `pri 18` to `/proc/<pid>/ctl`.
- Writes `enable` to watchdog device, then loops forever:
  - sleeps 300 ms,
  - seeks to start,
  - writes `restart`.

Important details:
- Designed around a watchdog timeout and CPU-speed comment: “allows 4.2GHz CPU, with some slop”.
- Uses `sysfatal` on failures.

Filesystem relevance:
- Direct Plan 9 namespace/device-file interaction with `/proc` and `#w`, but not filesystem implementation logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/watchdog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/write.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/write.c

Simple deterministic stdout data generator.

Key behavior:
- Fills a 1024-byte buffer with repeated 64-byte alphabet/digit pattern.
- Stores the current block offset high/low bytes into the first two bytes of each 64-byte chunk.
- Writes the 1024-byte buffer to stdout repeatedly.
- Default repeat count is 2560; optional first argument overrides it.

Use:
- Likely a test/load generator for pipes, devices, or file writes.

Filesystem relevance:
- Indirect test utility for write paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/zerotrunc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/zerotrunc.c

Filter that copies stdin to stdout until the first zero byte.

Key behavior:
- Reads up to 4096-byte chunks.
- Uses `memchr` to find NUL.
- Writes bytes before the first NUL, then stops.
- If no NUL appears, streams all input until EOF.

Use:
- Useful for truncating NUL-padded data or strings embedded in fixed-size binary fields.

Filesystem relevance:
- Indirect utility for stream/file content processing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/zerotrunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awd.c

Acme window-directory helper.

Key behavior:
- Opens `/dev/acme/ctl`; exits silently if acme is not available.
- Gets current working directory, removes trailing slash.
- Writes acme control commands in single writes using `xfprint()`:
  - `name <cwd>/-<arg-or-rc>`
  - `dumpdir <cwd>`
- `xfprint()` uses `vsmprint` then one `write()` so commands are not split by buffered `fprint`.

Filesystem relevance:
- Direct namespace interaction with `/dev/acme/ctl` and current working directory, but not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awk.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awk.h

Core Plan 9 awk interpreter header.

Key definitions:
- `Awkfloat` as `double`, `uschar`, `xfree`, and debug macro `dprintf`.
- Global interpreter state:
  - compile/run mode,
  - safe mode,
  - record and field state,
  - standard awk variables `FS`, `RS`, `ORS`, `OFS`, `OFMT`, `NR`, `FNR`, `NF`, `FILENAME`, `SUBSEP`, `RSTART`, `RLENGTH`,
  - regex match globals `patbeg` and `patlen`.
- `Cell`: variable/constant/function/field value with string, numeric value, type flags, and hash-chain link.
- `Array`: symbol table hash table.
- `Node`: parse-tree node with variable-length argument array.
- Type flags for numeric/string/array/function/field/record/constant storage.
- Builtin function IDs for length, sqrt, exp, log, int, system, rand/srand, sin/cos/atan, toupper/tolower, fflush, and utf.
- Cell subtypes, boolean subtypes, jump subtypes, node types, and helper macros for type tests.

Integration:
- Includes `proto.h` for interpreter function prototypes.
- Shared by parser, runtime, symbol table, regex, and execution modules.

Filesystem relevance:
- Indirect: awk can process files/streams, but this header is interpreter state, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.c

Generated yacc parser for the Plan 9 awk grammar, from `/sys/src/cmd/awk/awkgram.y`.

Key behavior:
- Defines parser semantic type `YYSTYPE` carrying `Node*`, `Cell*`, `int`, or `char*`.
- Defines awk grammar tokens from `PROGRAM` through `LASTTOKEN`, including statements, regex tokens, operators, builtins, variables, literals, getline, function calls, and control-flow tokens.
- Maintains parser state:
  - `beginloc`
  - `endloc`
  - `infunc`
  - `inloop`
  - `curfname`
  - `arglist`
- Provides helpers:
  - `setfname()` rejects redefining arrays/functions as functions.
  - `constnode()` detects constant parse nodes.
  - `strnode()` extracts string value.
  - `notnull()` converts expressions to explicit non-null tests where needed.
  - `checkdup()` rejects duplicate function arguments.
  - `yywrap()` returns EOF.
- Contains yacc tables:
  - `yyexca`, `yyact`, `yypact`, `yypgo`, `yyr1`, `yyr2`, `yychk`, `yydef`, token maps.
- Implements Plan 9 yacc runtime parser `yyparse()` with stack depth 150, error recovery, debug hooks, and token translation through `yylex1()`.

Semantic actions:
- Builds top-level program node from begin, pattern/action, and end lists.
- Tracks loop nesting for `for`, `while`, and `do`; rejects `break`/`continue` outside loops.
- Tracks function nesting; rejects `next`/`nextfile` inside functions.
- Builds parse tree nodes with `stat*`, `op*`, `linkum`, `pa2stat`, `exptostat`, `celltonode`, `rectonode`, `makearr`, and `itonp`.
- Compiles constant regex operands immediately through `makedfa`/`compre`.
- Handles safe-mode restrictions for command pipes, `getline` from commands, and redirected/pipe print forms.
- Builds AST for awk expressions, ternary, boolean operators, match/notmatch, `in`, concatenation, arithmetic, assignment forms, increments/decrements, field indirection, arrays, function calls, builtins, `split`, `substr`, `sub`, `gsub`, `index`, `match`, and `getline`.

Important details:
- This is generated code and should normally be regenerated from `awkgram.y`, not hand-edited.
- Uses token values starting at Plan 9 yacc private range `57346`.
- Filesystem relevance is indirect: awk’s parser supports file/pipe-oriented language constructs, but this file is parser implementation, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.c -->