# Group Research: group_66_9front_sources_os_plan9_9front_sys_src_cmd_aux_vga_bt485_c_sources_os_85414b734da4

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/bt485.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/bt485.c

Implements the Brooktree Bt485 RAMDAC controller, assuming an S3 86C928-style indirect DAC wiring. It exposes `bt485i`/`bt485o` helpers that route direct and indirect registers through VGA CRT register `0x55` and the shared `dacxreg` mapping.

The controller advertises enhanced, clock-doubler, external SID, and 32-bit SID capabilities. `init` derives a speed grade from names like `bt485-135`, validates or halves the requested pixel clock, and calls `resyncinit` when clock doubling changes shared controller assumptions.

`load` sleeps the DAC, selects enhanced pixel-port/clock-doubler state, configures multiplexing and command registers, then wakes the DAC. `dump` prints the direct register set plus indirect `Cmd3` and `Cmd4`.

Filesystem relevance is indirect: this is user-space Plan 9 hardware setup code that writes VGA I/O ports via the shared aux/vga framework, not storage or filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/bt485.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ch9294.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ch9294.c

Implements clock selection for the Chrontel CH9294 dual enhanced graphics clock generator. It contains static frequency tables for Tseng, S3/IIT, and Avance Logic pattern variants selected from controller names such as `ch9294-g`.

`init` chooses the closest supported clock index and optional divisor, using the primary video controller’s `Hclkdiv` capability to allow divisors up to 8. It fails if the best match is outside a 5% tolerance.

No hardware `load` routine is present; the selected index/divisor are communicated through `vga->i[0]` and `vga->d[0]` for the paired controller to use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ch9294.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd542x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd542x.c

Implements Cirrus Logic CL-GD542x/543x-style VGA controller setup. It unlocks extended sequencer registers, snarfs extended sequencer/graphics/CRT registers, reads the hidden DAC register, identifies chip IDs, and determines memory size plus possible PCI linear aperture support.

`clgd54xxclock` brute-forces Cirrus PLL numerator/denominator/post-divisor values against `RefFreq`. `init` validates the requested pixel clock against chip-family limits, programs VCLK3, sets depth-dependent pixel format and DAC mode, computes overflow bits, handles interlace, and marks high-memory graphics mode state.

`load` writes the computed sequencer, hidden DAC, CRT, and graphics registers. `clgd542xhwgc` is a registered but empty hardware-cursor placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd542x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd546x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd546x.c

Implements Cirrus Logic Laguna CL-GD546x PCI controller support. It finds supported Cirrus PCI device IDs, attaches MMIO, records frame-buffer aperture sizing, saves VGA extended registers, and snapshots Laguna-specific MMIO registers such as format, threshold, tiling, vendor-specific control, and 2D control.

`init` supports only 8-bit modes despite containing partial format branches for deeper modes. It reuses `clgd54xxclock`, computes CRT overflow bits, optionally enables linear mode, and configures tile/fetch/interleave control from resolution and memory-bank count.

`load` writes sequencer/CRT/graphics registers and the Laguna MMIO registers. `clgd546xhwgc` is an empty hardware-cursor registration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd546x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ct65540.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ct65540.c

Implements Chips & Technologies CT65540/CT65545 indexed extension-register support through ports `0x3D6/0x3D7`. Register groups are organized for snarf/dump output: misc, map, compatibility, clock, multimedia, alternate, and flat-panel registers.

`setclock` brute-forces PLL `m/n/p` values for requested mode frequencies up to 220 MHz. `init` supports 8-bit linear/sequential mode and lower-depth planar fallback, computes extended horizontal and vertical overflow bits, adjusts VGA sequencer/graphics/CRT state, and invokes clock programming.

`load` writes write-protect and clock-select registers first, then writes all grouped extension registers. It registers `ct65540`, `ct65545`, and an empty `ct65545hwgc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ct65540.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/cyber938x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/cyber938x.c

Implements Trident Cyber938x-family setup. It includes DAC Pixel Command Register access via the classic four-read Pixmask unlock sequence and stores old/new sequencer state plus inferred LCD panel dimensions.

`snarf` switches between old/new register modes, captures sequencer/CRT/graphics ranges, determines VRAM size from CRTC bits, and infers panel size from graphics register `0x52`. `init` enables linear mode if requested, sets scaling selectors by vertical size, configures pixel bus/PCR values for 8/16/24 bpp, and applies revision-specific register tweaks for Cyber/ProVidia/CyberBlade variants.

`load` switches the chip into new mode, writes PCR, graphics, CRT, and linear-aperture bits. `dump` prints extended register ranges, VCLK decoding, and LCD size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/cyber938x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/data.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/data.c

Defines global aux/vga state and the controller registry. `cflag` disables hardware cursor use; `dflag` controls palette behavior.

`ctlrs[]` is the central dispatch table of all supported VGA controllers, RAMDACs, clocks, VESA paths, and hardware cursor modules. The files in this group contribute entries such as `bt485`, `ch9294`, `clgd542x`, `igfx`, `mach64xx`, and `mga2164w`.

`dacxreg[4]` maps low two indirect DAC address bits onto VGA palette/mask register ports, used by RAMDAC implementations such as `bt485`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/db.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/db.c

Implements Plan 9 `ndb` parsing for `/lib/vgadb`-style controller and monitor definitions. It opens databases, builds linked `Attr` lists, looks up attribute values, and creates per-VGA linked copies of controller descriptors from `ctlrs[]`.

`dbctlr` identifies hardware by BIOS strings or PCI IDs, preferring BIOS matches over PCI matches, then saves controllers, RAMDACs, clocks, hwgc modules, linear settings, memory bandwidth, and additional attributes into `Vga`.

`dbmode` and `dbmonitor` resolve monitor timings, aliases, includes, size/depth parsing, optional `@NMHz` clock overrides, sync/interlace flags, and inherited video bandwidth. `dbdumpmode` prints the resolved `Mode`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/edid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/edid.c

Parses 128-byte VESA EDID blocks into `Edid` and `Modelist` data. It validates the EDID header and checksum, decodes manufacturer/product/serial/date/display features, and records DPMS/digital/monochrome/GTF flags.

It builds modes from detailed timing blocks first, then standard timings, descriptor-supplied extra timings, and established VESA timings. `edidshift` repairs buffers where the EDID header appears wrapped rather than at byte zero, useful for some Intel access paths.

`printedid` emits monitor identity, range limits, flags, and decoded modes. The mode output is consumed by `main.c` as a fallback when the monitor database lacks the requested mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/edid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/error.c

Provides fatal `error` and verbose `trace` helpers. `error` re-enables the sequencer, prefixes messages with `argv0`, optionally mirrors details to stdout when verbose, writes to stderr, and exits with `"error"`.

`trace` prints only when `vflag` or `Vflag` is active, resets register-dump line formatting when needed, and mirrors to the console with `print` when `Vflag` is set.

This file is central to failure handling across all hardware probing and register programming paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000.c

Implements Tseng ET4000 and ET4000-W32 setup. `snarf` unlocks ET4000 extended registers, saves sequencer/CRT/attribute extensions, and derives memory size, including W32-specific doubling.

`options` marks interlace as ET4000-specific uppercase `V`, enables clock dividers, and advertises 2x8 pixel-clock support on W32. `init` supports only <=8 bpp, optionally recomputes half-width timings for 2x8 mode, sets vertical/horizontal overflow, disables MMU/linear/MMIO buffers, selects clock index/divisor, and configures attributes.

`load` writes the ET4000 extended CRT, sequencer, and attribute registers. `dump` can also decode timing fields and prints W32 sprite/IMA registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000hwgc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000hwgc.c

Registers hardware cursor eligibility for ET4000-W32. `init` marks itself initialized, then disables hardware cursor globally via `cflag` unless the active controller name starts with `et4000-w32`, the mode is 8 bpp, and 2x8-bit pixel mode is not active.

It does not program cursor registers directly; it gates later hwgc selection in `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/et4000hwgc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode.c

Implements AMD Geode display controller setup using PCI MMIO plus MSR clock programming. `snarf` finds device `1022:2081`, attaches `geodemmio`, saves display-controller registers and clock MSR `0x4C000015`, and records a few VGA CRTC extension values.

`init` chooses low- or average-bandwidth preset registers by width, enables FIFO/display/timing/palette bypass, sets display mode by bpp, programs horizontal/vertical timing registers, line pitch, framebuffer active size, and looks up the exact pixel clock in `geode_modes.h`.

`load` writes the selected clock MSR, unlocks the display controller, and programs timing/config registers. `geodehwgc` is an empty placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode_modes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode_modes.h

Contains `NumModes = 61` and a static `geode_modes` lookup table mapping Geode clock MSR selector words to exact pixel-clock frequencies.

`geode.c` requires an exact frequency match in this table; unknown mode clocks are rejected rather than approximated. The table spans common VGA through high-resolution pixel clocks from about 24.923 MHz to 341.349 MHz.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode_modes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/hiqvideo.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/hiqvideo.c

Implements Chips & Technologies HiQVideo/HiQV32 PCI controller setup for devices including 69000 and 65550/65554/65555. It snarfs flat-panel, multimedia, configuration, and CRTC extension registers and determines max clock/memory size from PCI ID, voltage, and extension state.

The clock routine brute-forces PLL `M/N`, post divisor, and reference divisor under HiQVideo constraints. `init` supports 8/16/32 bpp, avoids DCLK programming for LCD output, handles standard VGA clocks specially, computes extended CRTC overflow fields, sets color-depth registers, and enables linear aperture when requested.

`load` synchronizes with vertical retrace, programs PLL registers when needed, writes extended CRTC/XR/FR state, and sets linear base registers. `dump` decodes VCLK and MCLK values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/hiqvideo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/i81x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/i81x.c

Implements early Intel 81x/830M integrated graphics setup. `snarf` locates supported Intel PCI device IDs, attaches GC MMIO, records AGP aperture sizing, captures VGA CRT/graphics/attribute registers, clock control registers, i830 LCD CRTC registers, and pixel pipeline control.

`i81xdclk` computes a DCLK divisor using a default mode frequency and 24 MHz reference. `init` supports selected virtual widths, configures pixel pipeline format for 8/16/24/32 bpp, optionally enables linear mapping, builds CRTC timing/start-address registers, and contains hardware-specific comments for values that “should” work but historically did not.

`load` writes VGA and MMIO clock/LCD/pixconf registers, initializes DAC mask/palette entries, and marks the controller loaded. `i81xhwgc` is an empty placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/i81x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ibm8514.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ibm8514.c

Defines IBM 8514/A graphics coprocessor I/O ports and multifunction indexes. It has no snarf/init path; `load` resets the subsystem, sets foreground/background mix modes, configures scissors bounds from framebuffer geometry, sets full write mask, and selects pixel control.

`dump` prints `Advfunc` and `Subsys` register values. This is accelerator-side initialization used alongside VGA mode setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ibm8514.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/icd2061a.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/icd2061a.c

Computes PLL parameters for the IC Designs ICD2061A dual programmable clock generator. It validates <=8 bpp, scales the requested clock into the 50-120 MHz VCO range, chooses the VCO range index, and brute-forces denominator/numerator values under reference-frequency constraints.

The resulting divider fields are stored in `vga->d[0]`, `vga->n[0]`, `vga->p[0]`, and `vga->i[0]`. This file does not serially load the clock itself; it supplies computed parameters to paired hardware code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/icd2061a.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics2494.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics2494.c

Implements table-based selection for ICS2494/ICS2494A dual video/memory clock generators. Pattern sets are selected from controller-name suffixes such as `ics2494-237`, `ics2494-304`, or `ics2494-324`.

`init` chooses a table index and optional power-of-two divisor, permitting divisors up to 8 if the active VGA controller advertises `Hclkdiv`. It requires a match within 1 MHz and stores the result in `vga->i[0]` and `vga->d[0]`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics2494.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics534x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics534x.c

Implements ICS534x GENDAC support for ET4000-W32p and ARK2000pv pairings. It toggles board-specific RS2 access through either CRTC `0x31` or sequencer `0x1C`, and errors if used with an unsupported controller.

`options` advertises 2x8 pixel-clock support. `init` derives speed grade from name, validates pclk, may halve pclk and resync for 2x8 mode, and either selects standard VGA clocks or brute-forces GENDAC PLL `M/N/R`.

`load` enters snooze/color mode, writes PLL f7 parameters when needed while preserving memory-clock control, sets pixel mode, restores RS2, and marks loaded. `dump` prints all PLL slots and decoded frequencies.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ics534x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/igfx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/igfx.c

Implements modern Intel integrated graphics support for G45, Ironlake, Sandy Bridge, Ivy Bridge, and Haswell-style devices. It models DPLLs, transcoders, FDI, panel fitters, planes, cursors, HDMI, DisplayPort, GMBUS, and AUX state in structured register snapshots.

`snarf` identifies Intel PCI IDs, attaches MMIO, captures generation-specific display registers, maps pipes/fitters/DPLLs, and reads EDID over GMBUS for VGA/LVDS or DisplayPort AUX/DPCD for DP/HDMI-style ports. EDID modes are annotated with `display` and sometimes `lcd` attributes for later mode selection.

`init` supports 32 bpp only. It disables legacy VGA and all active pipes/ports, selects the requested display port from mode attributes, computes PLLs, link M/N values, lanes, DDI/DP/HDMI/LVDS controls, plane stride, cursor-off state, and pipe/transcoder timings.

`load` powers panels down, disables ports/pipes, may extend GTT mappings for the requested framebuffer size, programs clock sources and DPLLs, enables pipes, writes plane/cursor state, enables ports, and trains DisplayPort links over AUX. This is the most complete display pipeline implementation in the group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/igfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/io.c

Provides shared low-level Plan 9 device access for aux/vga. It lazily opens `#P/iob`, `#P/iow`, `#P/iol`, and `#P/msr` for byte/word/long port I/O and MSR reads/writes, plus `#v/vgactl` for VGA control messages.

It parses cached `vgactl` attributes, writes control settings such as type, size, linear aperture, and PCI device, reads BIOS memory from `/dev/realmodemem` or `#P/realmodemem`, and supports BIOS hex dumps.

Utility functions include zeroing allocator `alloc`, palette writes, formatted register/item output, and controller flag printing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach32.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach32.c

Implements older ATI Mach32 VGA-mode setup without accelerator support. It accesses ATI extended registers through index port `0x1CE`, unlocks multiple protection bits, saves selected extended and coprocessor registers, and derives memory size from the miscellaneous register.

`init` selects one of a small common fixed-clock table, configures 8-bit linear-style VGA register state, sets clock index bits, handles interlace, and disables the 128 KB CPU aperture bit to keep a 64 KB VGA aperture.

Notable issue: `atixinit` calls `alloc(sizeof(mach32))` where `mach32` is a pointer variable, underallocating the `Mach32` structure that `snarf` later fills. `load` disables linear/memory-boundary state and writes selected extended registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64.c

Implements a simple ATI Mach64 path similar to `mach32.c`, with fixed-clock table assumptions rather than full programmable support. It initializes ATI extended-register access, saves selected extended registers and 32-bit config/memory/scratch registers, and derives memory size from `Memcntl`.

`init` assumes the ATI18818 clock table, finds a clock within 1 MHz with optional divide-by-two, configures 8-bit VGA register state, sets clock bits, handles interlace, disables the 128 KB CPU aperture bit, sets `ctlr->type` to `mach32`, and clamps VGA-mode visible memory to 1 MB.

`load` writes selected extended registers and `MiscW`. More complete Mach64-family support is in `mach64xx.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64xx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64xx.c

Implements broader ATI Mach64/Rage-family support using either legacy I/O register offsets or PCI I/O register mappings. It models CRTC, DAC, LCD, TV, PLL, DSP, memory, drawing, cursor, and configuration registers, with register-name tables for dumps.

`snarf` chooses port vs PCI register access, captures all core registers and PLLs, detects LT/LCD variants, reads LCD registers and panel ID, determines memory-size encoding, and sets framebuffer size plus preferred aperture alignment/size.

`init` handles depths from 1 through 32 bpp with PCI required for >8 bpp, detects enhanced Rage chips, computes/keeps PLLs, configures timing registers, pixel widths, linear aperture eligibility, LCD stretch state, and DSP FIFO parameters from BIOS memory-clock data when enhanced. `load` unlocks CRTC/LCD, programs aperture, timings, LCD registers, DAC/DSP/PLL state, initializes true-color palette grayscale when needed, and marks loaded.

`dump` prints register/PLL/LCD state, decodes VCLKs and pixel clock, and emits ATI BIOS clock/panel table information once. `mach64xxhwgc` is an empty placeholder.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mach64xx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/main.c

Contains the `aux/vga` command entry point and orchestration flow. It parses flags for BIOS string override, dump, init, load, palette, refresh, monitor/db selection, tilt, verbosity, and mode/virtual-size arguments.

The command identifies the controller through `dbctlr` or VESA fallback, snarfs all linked controllers, resolves modes from VESA, monitor database, or EDID, computes default frequency from video/memory bandwidth when needed, runs controller `options` and `init`, assigns a Plan 9 channel string, and optionally dumps state.

For load mode, it validates framebuffer size, sets draw-device type, configures linear aperture, writes draw size, disables the display sequencer around non-VESA register loads, runs each controller `load`, calls `drawinit`, selects hardware or software cursor, writes actual size and tilt, then exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga2164w.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga2164w.c

Implements Matrox Millennium/Millennium II MGA-2064W/MGA-2164W support with TI TVP3026 RAMDAC. It locates Matrox PCI devices, attaches MMIO/control and framebuffer segments, accesses TVP3026 direct/indexed registers through the RAMDAC aperture, and reads CRTC extension/config/PLL state.

`snarf` probes installed VRAM in 2 MB increments by writing test bytes through the mapped framebuffer and flushing the cache register. `options` rounds virtual width up to a 128-pixel boundary.

`init` forces linear mode, currently rejects >8 bpp, programs VGA/MGA CRTC extension timing, TVP registers, vertical blanking corrections, pixel and loop clocks, and Matrox option bits. It disables the generic VGA load path to control register programming order. `load` writes CRTC extensions, PCI option, VGA registers, PCLK/LCLK PLLs, and TVP registers in a strict order. `mga2164whwgc` only reuses `dump`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga2164w.c -->