# Group Research: group_68_9front_sources_os_plan9_9front_sys_src_cmd_aux_vga_sc15025_c_sources__752cdc5c9135

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/sc15025.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/sc15025.c

Implements the Sierra SC15025/SC15026 HiCOLOR-24 RAMDAC controller for Plan 9 `aux/vga`.

Key responsibilities:
- Provides RAMDAC command register access through VGA palette/pixel mask I/O sequencing.
- Parses optional speed-grade suffix from `ctlr->name` and validates requested pixel clock.
- Programs the DAC auxiliary register and command bits during `load`.
- Dumps the command register and indexed DAC registers `0x08..0x10`.

Important interfaces:
- Exports `Ctlr sc15025`.
- Uses `inportb`, `outportb`, `printitem`, `printreg`, and `error` from the `aux/vga` support layer.
- Sets `Foptions`; validates/sets `vga->f[0]`.

Notes:
- `pixmask`, `commandrw`, `commandr`, and `commandw` implement the DAC-specific access ritual.
- The 8-bit mode auxiliary setting is present but disabled in a commented block.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/sc15025.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/stg1702.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/stg1702.c

Implements the SGS-Thomson STG1702 enhanced true-color palette DAC controller.

Key responsibilities:
- Defines direct/index register constants for command, pixel mode, pipeline, reset, and power management.
- Exposes pixel mask based command and indexed-register access helpers.
- Advertises `Hpclk2x8`, enabling 2x8-bit pixel mode when paired with a compatible graphics chip.
- Validates pixel clock limits for ordinary 8-bit and 2x8-bit modes.
- Programs primary/secondary pixel mode and pipeline timing before writing the final command register.

Important interfaces:
- Exports `Ctlr stg1702`.
- Uses `vga->ctlr->flag & Hpclk2x8` to decide whether high-clock 2x8 mode is available.
- Calls `resyncinit(vga, ctlr, Upclk2x8, 0)` when it halves the requested clock for 2x8 operation.

Notes:
- Pixel clock below 16 MHz or above supported DAC speed is rejected.
- Dump reads company/device and indexed registers via the same pixel mask sequence.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/stg1702.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/t2r4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/t2r4.c

Implements the Number Nine Ticket to Ride IV controller.

Key responsibilities:
- Defines `T2r4` private state with PCI device, I/O base, MMIO mapping, saved I/O registers, global registers, and memory-window registers.
- Detects the PCI device, enables VGA PCI control, attaches the MMIO segment, and exposes video memory size.
- Captures/restores controller state across global CRT registers and memory window registers.
- Computes timing register values from `Mode` geometry, depth, and optional `zoom` attribute.
- Sets up a linear frame buffer window and display pitch for 8, 16, or 32 bpp.
- Bridges RGB524 RAMDAC access through T2R4 MMIO by installing `rgb524mnxi`/`rgb524mnxo` callbacks.

Important interfaces:
- Exports `Ctlr t2r4` and stub `Ctlr t2r4hwgc`.
- Uses `pcimatch`, `vgactlpci`, `vgactlw`, `segattach`, `inportl`, `outportl`.
- Uses `vga->private` to share private controller state between phases.

Notes:
- `snarf` mutates several configuration registers before reading MMIO state.
- `load` writes CRT/global/window registers, toggles `vgactl` for zoom, then reinitializes SGRAM with sleeps.
- `dump` prints saved I/O, global, and window register sets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/t2r4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/template.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/template.c

Provides a skeleton `aux/vga` controller implementation.

Key responsibilities:
- Shows the expected `snarf`, `options`, `init`, `load`, and `dump` function shape.
- Marks phase-completion flags `Fsnarf`, `Foptions`, `Finit`, and `Fload`.
- Exports a placeholder `Ctlr xxx`.

Important interfaces:
- Uses `USED` macros to silence unused-parameter warnings.

Notes:
- This is not a functional hardware driver; it is a source template for adding new VGA controllers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/template.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/trio64.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/trio64.c

Implements support for S3 Trio64 controllers and the Trio64 pixel clock PLL.

Key responsibilities:
- Unlocks and snarfs extended Trio sequencer and CRT registers.
- Advertises linear, enhanced, and 2x8 pixel clock capabilities.
- Implements `trio64clock`, the shared S3 PLL search used by Trio64 and ViRGE-family drivers.
- Programs VGA standard clock selection or DCLK PLL registers depending on requested frequency.
- Handles internal clock generator setup and optional 2x8 mode.
- Programs S3 advanced function register `0x4AE8` for enhanced mode.

Important interfaces:
- Exports `Ctlr trio64` and `void trio64clock(Vga*, Ctlr*)`.
- Relies on `s3generic` for base S3 register handling.
- Uses PLL fields in `Vga`: `f`, `m`, `n`, `r`, and `d`.

Notes:
- Rejects depths above 8 bpp in this Trio64 implementation.
- `trio64clock` searches M/N/R values and enforces roughly 0.5% output error.
- `dump` reconstructs and prints DCLK from saved PLL registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/trio64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3020.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3020.c

Implements TI TVP3020/3025/3026-style indexed RAMDAC access and base TVP3020 setup.

Key responsibilities:
- Provides direct and indexed register permission tables.
- Detects DAC ID through S3 CRT register `0x55` bank selection.
- Exports direct and indexed accessors: `tvp3020i`, `tvp3020xi`, `tvp3020o`, `tvp3020xo`.
- Validates indexed register access based on detected chip generation.
- Advertises clock doubler, external SID, parallel VRAM, and enhanced mode capabilities.
- Validates pixel clock, optionally halves it and requests `Uclk2`.
- Programs input/output clock selection, mux controls, auxiliary/color-key controls, sync polarity, and GPIO DAC selection.

Important interfaces:
- Exports `Ctlr tvp3020`.
- Uses `dacxreg[]`, `vgaxi`, `vgaxo`, `vgai`, `vgao`, `resyncinit`.
- Used by `tvp3025.c` as a base implementation.

Notes:
- Assumes attachment through S3 86C928 or S3 Vision964-style DAC bank selection.
- `dump` prints direct and indexed registers, substituting `0xFF` for inaccessible registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3020.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025.c

Specializes the TVP3020 support for TI TVP3025 RAMDACs.

Key responsibilities:
- Delegates options and initialization to `tvp3020`.
- Clears Bt485 emulation state through S3 CRT `0x5C` and TVP indexed registers.
- Runs the base TVP3020 load routine, then adjusts auxiliary control for enhanced mode.
- Dumps TVP3020-visible registers and TVP3025 PCLK/MCLK/RCLK PLL register groups.

Important interfaces:
- Exports `Ctlr tvp3025`.
- Calls `tvp3020.options`, `tvp3020.init`, `tvp3020.load`, and `tvp3020.dump`.
- Uses `tvp3020xi`/`tvp3020xo` for indexed DAC access.

Notes:
- `dumpclock` reconstructs clocks from `d`, `n`, and `p` register values.
- Comments note #9GXE64pro-specific use of CRT `0x5C` bit 5 as RS4.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025clock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025clock.c

Computes TVP3025 pixel clock PLL parameters.

Key responsibilities:
- If needed, initializes `vga->f[0]` from the display mode frequency.
- Brute-force searches divider `d`, multiplier `n`, and post-divider `p`.
- Enforces documented constraints for reference divider and VCO range.
- Stores the best parameters in `vga->d[0]`, `vga->n[0]`, and `vga->p[0]`.

Important interfaces:
- Exports `Ctlr tvp3025clock`.
- Provides only an `init` function; no direct load/dump phase.

Notes:
- The actual DAC programming is performed elsewhere; this file only calculates shared clock fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3025clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026.c

Implements TI TVP3026 RAMDAC register access and sync-polarity setup.

Key responsibilities:
- Provides TVP3026-specific direct/indexed register access, which differs from TVP3020/3025.
- Exports indexed accessors `tvp3026xi` and `tvp3026xo`.
- Advertises clock doubler, external SID, and enhanced mode capabilities.
- Validates pixel clock against name-derived speed grade.
- Requests clock doubling for 8-bit high-clock modes when needed.
- Programs general-control sync polarity and forces VGA misc sync bits off.

Important interfaces:
- Exports `Ctlr tvp3026`.
- Uses S3 CRT `0x55` bank selection and `dacxreg[]`.

Notes:
- The `Ctlr tvp3026` struct has `load` set to `0`, even though a static `load` function exists in the file. This means generic phase execution will not call that function unless wired elsewhere.
- `dump` prints direct registers, indexed registers, and decoded PCLK/MCLK/LCLK values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026clock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026clock.c

Computes TVP3026 pixel and loop clock PLL parameters.

Key responsibilities:
- Selects VGA standard clocks or external programmable-clock selection bits in `vga->misc`.
- Brute-force searches TVP3026 PCLK parameters `m`, `n`, and `p` under VCO constraints.
- Computes loop clock fields using enhanced-mode dependent factor `k`.
- Stores PCLK in `vga->m[0]`, `vga->n[0]`, `vga->p[0]`.
- Stores loop clock in `vga->m[1]`, `vga->n[1]`, `vga->p[1]`, `vga->q[1]`, and `vga->f[1]`.

Important interfaces:
- Exports `Ctlr tvp3026clock`.
- Provides only an `init` function.

Notes:
- Uses scaled arithmetic (`SCALE(f) ((f)/10)`) to reduce overflow risk in brute-force search.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/tvp3026clock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesa.c

Implements VESA BIOS Extension support for `aux/vga`.

Key responsibilities:
- Wraps real-mode VBE BIOS calls through `/dev/realmode` and `/dev/realmodemem`.
- Maintains a 1 MB memory shadow with page-valid/dirty tracking for real-mode buffers.
- Detects VBE 2.0+ support, enumerates VBE modes, queries mode information, and switches modes.
- Converts VBE framebuffer mode info into Plan 9 `Mode` records with size, channel, depth, stride, and VBE mode ID attributes.
- Supports explicit VBE mode IDs, mode scans, and fallback scanning of unoffered `0x100..0x1ff` modes.
- Reads DDC EDID using VBE function `0x4F15`.
- Handles Intel display selection/scaling extensions and has disabled NVIDIA scaling support due to a noted modeset breakage.
- Provides text-mode restore through `vesatextmode`.

Important interfaces:
- Exports `Ctlr vesa`, `Ctlr softhwgc`, `dbvesa`, `dbvesamode`, and `vesatextmode`.
- Uses `Vbe` private structure and `Vmode` intermediate mode representation.
- Integrates with `Vga` by installing `vga->vesa`, `vga->ctlr`, and a soft hardware cursor controller.

Notes:
- `load` resets scaling, optionally switches display output, sets VBE graphics mode with linear framebuffer/no-clear bits, then applies requested scaling.
- `rgbmask2chan` derives Plan 9 channel strings from VBE direct-color masks.
- `fixbios` patches a known Intel Cantiga mode alias table bug for 1440x900x32.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesadb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesadb.c

Provides built-in VESA DMT monitor timing definitions.

Key responsibilities:
- Defines static `Mode` records for common VESA DMT resolutions and refresh rates.
- Covers modes from 640x480 through 1920x1440, with horizontal/vertical totals, blanking, sync ranges, pixel clocks, and sync polarity.
- Exposes `Mode *vesamodes[]` as a null-terminated timing database.

Important interfaces:
- Used by `vesa.c` to populate timing fields for VBE modes when a matching resolution is found.
- Declared in `vga.h` as `extern Mode *vesamodes[]`.

Notes:
- The comments cite VESA Monitor Timing Standard DMT v1r08 and explain this database allows operation without `vgadb`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesadb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.c

Implements generic VGA register access and generic VGA mode programming.

Key responsibilities:
- Provides byte/indexed register helpers: `vgai`, `vgaxi`, `vgao`, `vgaxo`.
- Handles VGA attribute controller access sequencing through `Status1`.
- Snarfs baseline VGA state: misc, feature, sequencer, CRT, graphics, attribute, and optionally palette.
- Initializes generic VGA register state from a `Mode`, including sync polarity, sequencer setup, CRT timing, overflow bits, pitch, graphics controller, attribute controller, and palette.
- Loads generic VGA register state back to hardware.
- Dumps register sets and shared VGA timing/clock/memory metadata.

Important interfaces:
- Exports `Ctlr generic`.
- Uses constants and structures from `vga.h`.
- Calls `palette` controller methods when `dflag` is set.

Notes:
- CRT setup handles vertical interlace by halving vertical timing fields.
- The pitch calculation uses `vga->virtx`, matching comments in `vga.h` about virtual width correctness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.h

Defines the shared `aux/vga` controller model, register constants, data structures, flags, and extern declarations.

Key responsibilities:
- Defines standard VGA I/O ports, palette constants, reference clock constants, and name length.
- Defines `Ctlr` with phase callbacks `snarf`, `options`, `init`, `load`, `dump`.
- Defines controller phase/capability/use flags such as `Fsnarf`, `Hlinear`, `Ulinear`, `Hpclk2x8`, `Uclk2`.
- Defines `Attr`, `Mode`, `Modelist`, `Edid`, `Flag`, and the central `Vga` state structure.
- Documents how `mode->x/y` differ from `vga->virtx/virty`, including panning and stride alignment implications.
- Declares all controller instances and support functions across the `aux/vga` program.

Important interfaces:
- All files in this group include this header.
- Declares VESA entry points, VGA register helpers, PCI helpers, EDID helpers, RAMDAC helpers, S3 helpers, and many controller symbols.

Notes:
- The header is the primary integration contract for this controller framework.
- It includes a global `Biobuf stdout` declaration in the main section.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/virge.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/virge.c

Implements S3 Trio64+/ViRGE/Savage-family controller support.

Key responsibilities:
- Unlocks and snarfs extended S3 sequencer/CRT registers.
- Identifies specific chips by CRT ID registers `0x2D/0x2E`.
- Configures PLL limits, aperture size, and memory size by chip family.
- Handles Trio64+, Aurora64V+, Trio64V2, ViRGE, ViRGE/DX/GX/VX/GX2, Savage MX/MV, Savage4/IX, SuperSavage/IXC16, ProSavage variants.
- Rounds virtual width to a multiple of 16 for Savage-family stride requirements.
- Computes width, display mode bits, FIFO thresholds, MMIO mode, and color-mode fields for each chip family.
- Uses `trio64clock` for PLL search and maps results into chip-specific sequencer fields.
- Installs pairwise CRT/sequencer settings and advanced-function register state during `load`.
- Dumps extended CRT/sequencer registers plus DCLK/MCLK derived values.

Important interfaces:
- Exports `Ctlr virge`.
- Depends on `s3generic` and `trio64clock`.
- Uses optional `noclockset` mode attribute.

Notes:
- Contains many hardware-specific comments marking guessed or empirical settings.
- Includes a `newptk`-style safety equivalent for clocks? No; key safety is not here. The notable safeguards are pixel clock validation and optional `noclockset`.
- Supports higher depths for selected ViRGE/Savage variants, unlike `trio64.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/virge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision864.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision864.c

Implements S3 Vision864 controller support.

Key responsibilities:
- Delegates base snarf/init/load/dump to `s3generic`.
- Advertises linear, 2x8, enhanced-mode capabilities.
- Rejects depths above 8 bpp.
- Applies VL-bus adjustments when detected through CRT `0x36`.
- Programs display memory access registers, fetch start, and blank/skew delays.
- Chooses CRT `0x54` values heuristically by horizontal resolution.
- Writes S3 advanced-function register for enhanced mode.

Important interfaces:
- Exports `Ctlr vision864`.
- Uses mode attributes `delaybl` and `delaysc`.

Notes:
- Comments state this is close to 86C801/805 and “needs tuning”.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision864.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision964.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision964.c

Implements S3 Vision964 controller support.

Key responsibilities:
- Snarfs base S3 state plus CRT registers `0x22`, `0x24`, and `0x26`.
- Advertises linear and enhanced capabilities.
- Rejects depths above 8 bpp.
- Resynchronizes timings for enhanced mode, especially when RAMDAC clock doubling is active.
- Computes SID divide settings from RAMDAC bus width, clock doubling, and bits per pixel.
- Adjusts SAM size, display FIFO, CRT delay, VCLK phase, and enhanced-mode flags.
- Writes enhanced CRT registers and S3 advanced-function register.

Important interfaces:
- Exports `Ctlr vision964`.
- Depends on `s3generic`, RAMDAC capability flags such as `Hsid32` and `Uclk2`, and attributes `sam512`, `vclkphs`, `delaybl`, `delaysc`.

Notes:
- Primarily supports enhanced 8-bit modes with external RAMDAC cooperation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision964.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision968.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision968.c

Implements S3 Vision968 controller support.

Key responsibilities:
- Snarfs base S3 state plus extended sequencer and CRT ID/control registers.
- Advertises linear and enhanced capabilities.
- Rejects depths above 8 bpp.
- Resynchronizes horizontal timings for RAMDAC clock doubling or enhanced 8-bit mode.
- Computes optional external SID divide settings when RAMDAC supports `Hextsid`.
- Programs enhanced-mode CRT flags, SAM selection, DAC-related clock phase, blank/skew delays, and advanced-function output.

Important interfaces:
- Exports `Ctlr vision968`.
- Depends on `s3generic`, RAMDAC flags `Hextsid`, `Hsid32`, `Uclk2`, and attributes `disa1sc`, `vclkphs`, `delaybl`, `delaysc`.

Notes:
- Contains STB Velocity 64 Video-specific empirical handling around `disa1sc` and CRT `0x67`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision968.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vmware.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vmware.c

Implements VMware SVGA controller support.

Key responsibilities:
- Detects VMware video PCI device IDs `0x0710` and `0x0405`.
- Sets register address/data ports based on VMware SVGA version.
- Reads VMware SVGA register set into private `Vmware` state.
- Derives Plan 9 channel string from red/green/blue masks and host depth/bpp.
- Sets framebuffer base and aperture size from PCI BARs/registers.
- Validates VMware SVGA version 2, clips requested screen size to max dimensions, and forces mode depth/channel to device values.
- Programs width/height/enable/guest ID during load.
- Updates `/dev/vgactl` size when device stride differs from visible width.

Important interfaces:
- Exports `Ctlr vmware` and stub `Ctlr vmwarehwgc`.
- Uses `vgactlpci`, `vgactlw`, `outportl`, `inportl`.

Notes:
- The clock routine is intentionally empty.
- Uses linear/enhanced mode unconditionally after initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/vmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/w30c516.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/w30c516.c

Implements IC Works W30C516 ZOOMDAC support.

Key responsibilities:
- Defines indirect register indices for control, ID, image window, ratio, offset, and test registers.
- Advertises 2x8 pixel mode capability.
- Derives speed grade from controller name and validates pixel clock limits.
- Optionally halves the requested clock and requests `Upclk2x8` for compatible high-clock 8-bit modes.
- Puts the DAC to sleep, programs mode bits, and wakes it.
- Dumps all indirect registers through ATT DAC access helpers.

Important interfaces:
- Exports `Ctlr w30c516`.
- Uses `attdaci` and `attdaco` for indirect register access.
- Calls `resyncinit` when using 2x8 mode.

Notes:
- 8-bit 6/8-bit color selection is present but disabled by `&& 0`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/w30c516.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wacom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wacom.c

Implements a Plan 9 9P service that exposes a serial Wacom tablet as `/dev/tablet`.

Key responsibilities:
- Opens `/dev/eia2`, configures serial speed to 19200 baud, queries tablet capabilities, and reads screen size from `/dev/draw/new`.
- Parses Wacom packets into scaled x/y coordinates, button bits, and pressure.
- Formats events as `m x y buttons pressure\n`.
- Maintains per-reader queues and pending read requests.
- Broadcasts each tablet event to all open readers.
- Mounts a synthetic 9P service after forking background service processes.

Important interfaces:
- Uses `thread.h`/`9p.h` `Srv`, `Req`, `Fid`, `File`, and `alloctree/createfile`.
- Uses Plan 9 `Ref` for message reference counting and `Lock` for queue/reader protection.

Notes:
- `readpacket` scales raw tablet coordinates/pressure using queried maximums and current screen size.
- `tabletread` rejects concurrent reads on the same fid.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wacom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wikifmt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wikifmt.c

Implements a Google Code wiki syntax to HTML converter.

Key responsibilities:
- Reads all input into a growable buffer and writes buffered HTML to stdout.
- Parses headings, links/images, inline code, bold/italic/sup/sub/strike, preformatted/teletype blocks, tables, blockquotes, lists, horizontal rules, comments, and raw-looking HTML tags.
- Escapes `<`, `>`, and `&` in content contexts.
- Generates anchor names for headings.
- Handles automatic links for `http://`, `https://`, and `ftp://`.
- Uses recursive `body` parsing with global state for quote/list/table indentation.

Important interfaces:
- Standalone command with optional input file argument.
- Uses Plan 9 libc only.

Notes:
- Image detection is based on URL suffix `.png`, `.jpg`, or `.gif`.
- The parser is stateful and hand-rolled, not a general HTML sanitizer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wikifmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wpa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wpa.c

Implements WPA/WPA2 supplicant behavior for Plan 9 wireless devices.

Key responsibilities:
- Builds WPA/RSN information elements from kernel-reported BSS RSNE data.
- Chooses pairwise/group cipher support between TKIP and CCMP.
- Integrates with factotum for PSK, MSCHAPv2, identity lookup, PMK storage, and PTK derivation.
- Processes EAPOL Ethernet frames and implements WPA key handshake logic.
- Calculates and verifies EAPOL MICs using HMAC-MD5 or HMAC-SHA1 depending on key descriptor version.
- Unwraps encrypted key data using RC4 or AES key unwrap.
- Implements EAP Identity, MSCHAPv2, EAP-TTLS, and PEAP client paths.
- Tunnels TLS records through EAP fragmentation and derives PMK from TLS keying material.
- Installs pairwise and group keys by writing `rxkey`, `txkey`, and `rxkeyN` commands to the device control file.
- Reconnects after deassociation and can background itself.

Important interfaces:
- Talks to the network device through `dial(dev!0x888e, ..., devdir, &cfd)` and `ifstats`.
- Uses `/mnt/factotum/rpc` and `/mnt/factotum/ctl`.
- Uses libsec/libauth primitives: TLS, HMAC, AES, RC4, `auth_rpc`, `auth_respond`, `auth_getuserpasswd`.

Notes:
- `newptk` gates pairwise key installation to avoid reinstalling PTK on replayed retransmits.
- `lastrepc` rejects replay counters that do not strictly increase.
- `-1` forces WPA1/TKIP defaults, `-2` forces RSN/CCMP defaults, `-p` prompts/warms credentials, and `-s` sets ESSID.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/wpa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/write.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/write.c

Generates repeated patterned binary output.

Key responsibilities:
- Fills a 1024-byte buffer with repeated 64-byte pattern data.
- Stores the block offset in the first two bytes of each 64-byte chunk.
- Writes the 1024-byte buffer repeatedly to stdout.
- Accepts an optional iteration count; default is 2560.

Important interfaces:
- Standalone command using Plan 9 libc.

Notes:
- Useful as a deterministic stream generator for testing writes or throughput.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/zerotrunc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/zerotrunc.c

Copies stdin to stdout until the first zero byte.

Key responsibilities:
- Reads input in 4096-byte chunks.
- Searches each chunk for `'\0'`.
- Writes only bytes before the first zero byte.
- Stops after encountering a zero byte or EOF.

Important interfaces:
- Standalone Plan 9 libc command.

Notes:
- Intended for truncating null-terminated data streams without including the terminator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/zerotrunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/awk.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/awk.h

Defines core data structures, globals, constants, and macros for the Plan 9 awk implementation.

Key responsibilities:
- Defines `Awkfloat`, debug macros, record-size defaults, and standard `Biobuf` globals.
- Declares builtin variable pointers such as `FS`, `RS`, `ORS`, `OFS`, `NR`, `FNR`, `NF`, `FILENAME`, `SUBSEP`, `RSTART`, and `RLENGTH`.
- Defines `Cell`, the variable/value representation used for scalars, arrays, fields, constants, functions, and temporaries.
- Defines `Array`, the hash table representation for awk arrays and symbol tables.
- Defines `Node`, the parse-tree node representation.
- Defines cell flags, builtin function IDs, node types, ctype/csub values, and jump/bool classifications.
- Includes `proto.h`.

Important interfaces:
- Shared by lexer, parser, runtime, regex, I/O, and generated dispatch code.
- Provides macros like `isstr`, `isnum`, `isarr`, `isfcn`, `freeable`, and `notlegal`.

Notes:
- Carries Lucent copyright notice.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/awk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/awkgram.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/awkgram.y

Defines the yacc grammar for awk programs.

Key responsibilities:
- Declares awk tokens, semantic types, precedence, and grammar productions.
- Builds parse-tree nodes for programs, BEGIN/END blocks, pattern-action statements, functions, loops, conditionals, print/printf, getline, array tests, assignments, arithmetic, regex matches, split/sub/gsub, and builtins.
- Enforces safety restrictions for command pipes/redirections when `safe` is enabled.
- Tracks function and loop context to reject illegal nested functions, returns, break/continue, next/nextfile.
- Converts constant regex/string expressions into compiled regex nodes where possible.
- Defines helper functions `setfname`, `constnode`, `strnode`, `notnull`, and `checkdup`.

Important interfaces:
- Produces `yyparse` and token constants used by the rest of awk.
- Uses parse helpers from `parse.c`, regex compiler `compre`, and symbol/cell APIs.
- Updates globals `beginloc`, `endloc`, `winner`, `infunc`, `inloop`, `curfname`, and `arglist`.

Notes:
- `notnull` wraps non-boolean expressions as `expr != nullnode`.
- Function argument duplicate detection is performed during grammar reduction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/awkgram.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/lex.c

Implements the awk lexical scanner.

Key responsibilities:
- Tokenizes identifiers, keywords, numbers, strings, regular expressions, operators, braces, comments, and line continuations.
- Maintains `lineno`, brace/bracket/paren counts, pushback buffer, and error context buffer.
- Binary-searches sorted keyword table for awk keywords and builtins.
- Handles argument names inside function bodies.
- Parses string escapes including common escapes, octal, and hex.
- Supports `$` field references and indirect expressions.
- Provides `startreg`/`regexpr` for grammar-directed regex literal scanning.
- Reads lexical input either from inline program string or `pgetc()` program files.

Important interfaces:
- Exports `yylex`, `input`, `unput`, `unputstr`, `startreg`.
- Uses `setsymtab`, `tostring`, `to_number`, `adjbuf`, and parser token definitions from `y.tab.h`.

Notes:
- `sc` returns a synthetic semicolon before a closing brace, then returns `}` on the next scan.
- `safe` rejects `system`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/lib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/lib.c

Implements awk record/field handling, command-line variable handling, diagnostics, and numeric conversion helpers.

Key responsibilities:
- Initializes `$0`, field cells, record buffers, and field tables.
- Opens input files or stdin based on `ARGV`, processing command-line `var=value` assignments in order.
- Reads records according to `RS`, including blank-line paragraph behavior for empty `RS`.
- Splits records into fields based on default whitespace, single-character FS, empty FS as UTF character fields, or regex FS.
- Rebuilds `$0` from fields using `OFS` when fields are modified.
- Grows field tables dynamically.
- Implements error reporting with source/input context and brace/bracket/paren checks.
- Provides fatal/warning handlers and numeric parsing via integer/float logic.

Important interfaces:
- Exports `recinit`, `getrec`, `readrec`, `nextfile`, `fldbld`, `fieldadr`, `recbld`, `SYNTAX`, `FATAL`, `WARNING`, `to_number`, and related helpers.
- Uses regex APIs `compre`, `nematch`, `releasere`.
- Uses symbol APIs `lookup`, `setsval`, `setfval`, `setsymtab`, `getsval`.

Notes:
- `inputFS` snapshots FS at input time so later field splitting uses the correct separator.
- Error context printing relies on lexer buffer globals `ebuf` and `ep`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/main.c

Implements the Plan 9 awk command entry point.

Key responsibilities:
- Initializes floating-point control, standard `Biobuf`s, notification handler, PRNG seed, and symbol table.
- Parses options: `-safe`, `-f programfile`, `-F fieldsep`, `-v var=value`, and `-d`.
- Selects inline program text or one or more `-f` program files.
- Initializes records, built-in symbols, `ARGV`/`ARGC`, and then runs `yyparse`.
- Applies `-F` after parsing, then runs the compiled parse tree if no syntax error occurred.
- Provides `pgetc` to feed source characters to the lexer across multiple program files.
- Provides `cursource` for diagnostics.

Important interfaces:
- Calls `recinit`, `syminit`, `arginit`, `yyparse`, `run`, and `bracecheck`.
- Sets global `compile_time` to distinguish command-line, compile, and runtime phases.

Notes:
- `-F t` maps to tab as a historical awk wart.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/maketab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/maketab.c

Generates the awk token dispatch table used by the runtime executor.

Key responsibilities:
- Reads `y.tab.h` token definitions.
- Emits C source containing `printname[]`, `proctab[]`, and `tokname`.
- Maps grammar token IDs to runtime function names such as `arith`, `assign`, `boolop`, `program`, `getline`, `printstat`, and `jump`.
- Uses `nullproc` for tokens without runtime implementations.

Important interfaces:
- Consumes `y.tab.h`.
- Emits generated C intended to be compiled into awk.
- Depends on the `FIRSTTOKEN..LASTTOKEN` range.

Notes:
- This is a build-time helper, not part of awk runtime execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/maketab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/parse.c

Implements parse-tree construction helpers for awk.

Key responsibilities:
- Allocates variable-sized `Node` structures.
- Provides `node1` through `node4` and statement/expression wrappers `stat1..stat4`, `op1..op4`.
- Converts `Cell` objects to value nodes.
- Builds `$0` references with `rectonode`.
- Converts scalar cells into arrays on demand with `makearr`.
- Builds pattern-range state nodes with `pa2stat`.
- Links statement lists with `linkum`.
- Registers function definitions and records argument counts.
- Looks up function argument indexes.
- Provides pointer/integer conversion helpers for embedding small integers in `Node*` fields.

Important interfaces:
- Used heavily by `awkgram.y`.
- Uses globals `lineno`, `exitstatus`, `paircnt`, `pairstack`, and parser globals `arglist`.

Notes:
- Limits `pat,pat` range patterns to `PA2NUM` 50.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/popen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/popen.c

Implements awk pipe open/close support on Plan 9.

Key responsibilities:
- Provides `popen` by creating a pipe, forking, and executing `/bin/rc -c cmd`.
- Tracks up to `MAXFORKS` active child processes with fd, pid, done flag, and status text.
- Closes inherited file descriptors in the child after duplicating the pipe end.
- Provides `pclose` to close the `Biobuf`, wait for the matching child, and return command status.

Important interfaces:
- Exports `Biobuf *popen(char*, int)` and `int pclose(Biobuf*)`.
- Used by awk runtime redirection/pipe execution.

Notes:
- `pclose` waits broadly and records statuses for other tracked children it reaps along the way.
- Status buffer copy uses `strecpy` with an apparent `+512` bound despite `status[128]`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/popen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/proto.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/proto.h

Declares cross-file function prototypes for the awk implementation.

Key responsibilities:
- Declares parser, lexer, regex, main, parse-tree, symbol table, record/field, runtime execution, I/O redirection, substitution, and pipe functions.
- Provides the central compile-time interface between separately compiled awk modules.
- Declares generated dispatch table `proctab[]` and `tokname`.

Important interfaces:
- Included by `awk.h`, therefore shared across the awk source set.
- Covers modules not all present in this group, including `run.c` and `tran.c`.

Notes:
- The header carries the Lucent license block and uses Plan 9 C style declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/re.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/re.c

Provides awk’s interface to the Plan 9 regular-expression engine.

Key responsibilities:
- Preprocesses awk regex syntax into forms accepted by Plan 9 `regexp`.
- Handles special conversions for empty groups/classes, literal hyphens in classes, hex/octal escapes, and common escaped characters.
- Compiles regex patterns with `regcomp`.
- Maintains a small runtime cache of dynamic regex programs with use and in-use counters.
- Exposes match functions for boolean match, positioned match, and non-empty match.
- Updates global `patbeg` and `patlen` for functions such as `match`, `sub`, `gsub`, and field splitting.
- Provides `regerror` and `overflow` fatal handlers.

Important interfaces:
- Exports `compre`, `releasere`, `match`, `pmatch`, `nematch`, `hexstr`, and `quoted`.
- Uses Plan 9 `regexp.h` `Reprog`, `Resub`, `regcomp`, and `regexec`.

Notes:
- Cache is only used at runtime (`compile_time == 0`), not while compiling the awk program.
- `MAXRE` limits preprocessed regex size to 512 bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/re.c -->