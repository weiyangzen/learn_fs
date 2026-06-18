# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.c lines 8163-11379

## Scope

This chunk covers the late CRT2/video-bridge programming path for the SiS framebuffer driver. It starts inside Chrontel TV encoder setup, continues through Chrontel 7019 LCD/power sequencing, the central `SiS_SetCRT2Group()` mode-programming coordinator, SiS30x backlight helpers, bit-banged DDC/I2C helpers used for EDID and Chrontel register access, 315/330/661 OEM compensation policy, old-ROM LVDS finalization, and 300-series OEM LCD/TV tuning helpers.

The earlier part of `init301.c` computes mode, panel, TV, CRTC, FIFO, VCLK, and bridge register groups. This range applies the final programming decisions to hardware ports (`Part1`, `Part2`, `Part4`, SR/CR registers) and auxiliary I2C devices, then turns the CRT2 path back on.

## Purpose

The code in this range exists to finish secondary-display setup for legacy SiS chipsets and external video bridges. Its responsibilities are:

- Program Chrontel 7005 and 7019 TV/LCD encoder registers for NTSC, PAL, PAL-M, PAL-N, NTSC-J, overscan/underscan, SCART, and YPbPr-like output modes.
- Sequence Chrontel 7019 LVDS power, PLL, datapath, VSYNC, and backlight state for SIS_740 and SIS_650-class chips.
- Coordinate CRT2 register programming through `SiS_SetCRT2Group()`, including mode lookup, bridge disable/enable, register group setup, CRT1/CRT2 clock/sync changes, OEM patching, and final display enable.
- Expose backlight on/off helpers for SiS30xLV bridge hardware.
- Implement a private bit-banged I2C/DDC stack for Chrontel access, Trumpion programming, EDID probing, and EDID reads.
- Apply OEM delay compensation, TV anti-flicker, phase increment, Y-filter, edge enhancement, LCD dither/sync, and panel parameter policy from BIOS ROM tables, hard-coded chipset tables, custom PCI-subsystem rules, and user/detected PDC overrides.
- Preserve older BIOS compatibility with explicit LVDS finalization and 300-series OEM table selection.

## Important APIs, Types, and Functions

Primary externally visible functions in this chunk:

- `SiS_SetCRT2Group(struct SiS_Private *SiS_Pr, unsigned short ModeNo)` is the central CRT2 programming entry point exported through `init301.h` and `sis.h`. It searches mode tables, gets the refresh table index, computes CRT2 data, calls register-group writers, applies OEM/final LCD tweaks, enables the bridge, displays output, and locks CRT2 registers.
- `SiS_SiS30xBLOn()` and `SiS_SiS30xBLOff()` switch SiS30xLV LCD backlight bits in Part4 register `0x26`, including retrace and delay handling.
- `SiS_SetCH700x()`, `SiS_SetCH701x()`, `SiS_GetCH700x()`, `SiS_GetCH701x()`, and `SiS_SetCH70xxANDOR()` provide Chrontel encoder register access over the private DDC/I2C path.
- `SiS_Chrontel701xBLOn()` and `SiS_Chrontel701xBLOff()` control Chrontel 7019 panel backlight register `0x66`.
- `SiS_HandleDDC()` probes DDC capability or reads EDID/VDIF-style data for CRT1/CRT2 adapters, returning `0xffff` for errors, DDC mode flags for probe, or a checksum-style result for EDID reads.
- `SiS_ReadDDC1Bit()` reads a single DDC1 bit from SR11.

Important local functions:

- `SiS_SetCHTVReg()` tail selects a Chrontel TV register table based on TV mode and output standard, then writes Chrontel 7005 or 7019 registers with mode-specific and standard-specific adjustments.
- `SiS_SetCH701xForLCD()`, `SiS_ChrontelPowerSequencing()`, `SiS_ChrontelResetVSync()`, `SiS_ChrontelResetDB()`, `SiS_ChrontelInitTVVSync()`, `SiS_ChrontelDoSomething1/2/3()`, `SiS_Chrontel701xOn()`, and `SiS_Chrontel701xOff()` implement Chrontel 7019 LCD/TV power-up, reset, PLL, datapath, and VSYNC sequences.
- `SiS_SetupDDCN()`, `SiS_SetStart()`, `SiS_SetStop()`, `SiS_WriteDDC2Data()`, `SiS_ReadDDC2Data()`, `SiS_SetSCLKLow()`, `SiS_SetSCLKHigh()`, `SiS_CheckACK()`, `SiS_SendACK()`, `SiS_PrepareDDC()`, `SiS_ProbeDDC()`, and `SiS_ReadDDC()` form the generic bit-banged I2C/DDC layer.
- `SiS_SetTrumpionBlock()` and `SiS_SetTrumpBlockLoop()` write Trumpion panel controller blocks with repeated I2C attempts.
- `GetRAMDACromptr()`, `GetLCDromptr()`, `GetTVromptr()`, `GetLCDPtrIndexBIOS()`, `GetLCDPtrIndex()`, `GetTVPtrIndex()`, `GetOEMTVPtr661()`, and `GetOEMTVPtr661_2_OLD()` compute BIOS/table offsets for compensation and TV tuning.
- `SetDelayComp()`, `SetDelayComp661()`, `SetAntiFlicker()`, `SetEdgeEnhance()`, `SetYFilter()`, `SetPhaseIncr()`, `SetCRT2SyncDither661()`, and `SetPanelParms661()` implement 315/330/661-series OEM policy.
- `SiS_OEM310Setting()` and `SiS_OEM661Setting()` are wrappers called by `SiS_SetCRT2Group()` for late OEM register programming.
- `SiS_FinalizeLCD()` applies old-ROM LVDS register finalization, backup restoration, expansion/no-expansion tweaks, and panel-specific fixes.
- `SetOEMLCDData2()`, `GetOEMLCDPtr()`, `SetOEMLCDDelay()`, `SetOEMTVDelay()`, `SetOEMAntiFlicker()`, `SetOEMPhaseIncr()`, `SetOEMYFilter()`, `SiS_SearchVBModeID()`, and `SiS_OEM300Setting()` implement 300-series OEM handling.

Key state comes from `struct SiS_Private`: chip type, custom type, bridge type/info flags, panel resolution/info, TV mode, BIOS ROM pointer, ROM layout flags, mode tables, DDC bit masks and ports, Chrontel initialization flag, detected/user PDC values (`PDC`, `PDCA`), LCD high/low override (`LVDSHL`), backup Part1 registers, panel dimensions, and I/O port bases.

## Control Flow

Chrontel TV setup first maps the current TV standard and overscan flags to a Chrontel register table. For Chrontel 7005 (`SiS_IF_DEF_CH70xx == 1`) it supports only small modes through `resindex <= 5`, programs current and black-level values for PAL or NTSC, writes core mode/position registers, sets flicker/text/bandwidth registers, and adjusts FSCI/ACIV/loop-filter bits for specific 640x480 and 800x600 NTSC overscan/underscan cases. PAL avoids FSCI manipulation and uses ACIV.

For Chrontel 7019 (`SiS_IF_DEF_CH70xx != 1`) it supports `resindex <= 6`, writes a longer mode table to registers `0x00` through `0x10` plus scattered Chrontel registers, applies NTSC-J overrides, and adjusts register `0x21` for PAL-N or NTSC-J CIV behavior. Chrontel 7019 LCD helpers then use resolution and chipset-specific tables to set LVDS registers, skip rewriting if register `0x73/0x74` already match the target panel, program power sequencing, and perform SIS_740-specific datapath and Part1 adjustments.

`SiS_SetCRT2Group()` is the main bridge mode-set flow. It marks `ProgrammingCRT2`, searches the mode table unless a custom mode is active, selects a CRT2 refresh rate, unlocks CRT2, saves CRT2 state, and optionally disables the bridge before programming. If CRT2 output is disabled, it locks and returns after turning the display on.

For active CRT2 output, `SiS_SetCRT2Group()` computes mode data with `SiS_GetCRT2Data()` and panel-link data with `SiS_GetLVDSDesData()` where needed. With SiS video bridges it writes Group1, Group2, C/ELV Group2, Group3, Group4, C/ELV Group4, Group5, sync, CRT1 CRTC modification, and ECLK as required by bridge type and LCD path. Without SiS bridge hardware, it programs sync, CRT1 CRTC, ECLK, Chrontel LCD tables, and Chrontel TV registers. After group programming it applies 300-series OEM settings, 315/330 LCD finalization and OEM settings, or 661+ OEM settings. It then enables the bridge, turns the display on, performs Chrontel 7005 LCD-vs-TV mutual exclusion, locks CRT2 on low-mode-test paths, and returns success.

The bit-banged I2C/DDC flow is shared by Chrontel access and EDID. `SiS_InitDDCRegs()` chooses the DDC port/index/data/clock bit masks from adapter number, VGA engine, bridge flags, and CR32 output-detection bits. `SiS_SetStart()` and `SiS_SetStop()` generate I2C start/stop transitions; byte write and read functions toggle SCLK and SD bits using `SiS_SetRegANDOR()`. `SiS_SetSCLKHigh()` includes a watchdog loop for clock stretching or stuck-low clock lines. Chrontel register writes and reads retry up to 20 times, mark `SiS_ChrontelInit` after success, and for Chrontel 700x fall back from SR11 bit masks to index `0x0a` masks if the first bus mapping fails.

`SiS_HandleDDC()` validates adapter and DDC type, initializes the DDC bus, temporarily adjusts SR1F and, for 300-series VGA, CR17/SR00 to ensure display state is suitable for DDC. It waits through retraces when needed, then either probes addresses `0xa0`, `0xa2`, and `0xa6`, or reads 128/256 bytes into the caller buffer. EDID reads validate the EDID header and version for DDC type 1 and can return `0xfffe` when analog/digital EDID type does not match the requested adapter unless `DDCPortMixup` is set. Original SR/CR state is restored before return.

OEM setting flow is table-driven with BIOS fallback. `SetDelayComp()` handles pre-661 chips: VGA2, LCD/LCDA, and TV each choose delay from user/detected PDC, custom panel dimensions, hard-coded subsystem cases, old ROM pointers, chipset/bridge tables, or LVDS defaults. `SetDelayComp661()` adds new-ROM logic, clock-derived index selection, 661/760 ROM tables, XGI defaults, UMC offset handling, and LCD struct pointers. TV helpers choose anti-flicker, edge enhancement, Y-filter, and phase increment values from ROM tables or static tables and write Part2 filter/phase registers. `SiS_OEM310Setting()` and `SiS_OEM661Setting()` assemble those helpers based on bridge type and active output.

`SiS_FinalizeLCD()` only runs for old-ROM LVDS paths on 315-class chips. It applies `LVDSHL` if present, skips custom panels/custom modes and certain OEM machines, obtains standard or extended mode flags, and then handles many panel-specific register corrections. For 1024x768 LCDA it may restore backed-up Part1 registers if `Backup_Mode` matches; otherwise it writes expansion/no-expansion values. For non-LCDA LCD paths it adjusts Part2 vertical display-end timing using current Part2 state, panel resolution, VESA timing flag, and VGA vertical display size.

The 300-series OEM path finds a `SiS_VBModeIDTable` entry with `SiS_SearchVBModeID()`, with special mode aliases for low VGA modes and 350/400-line variants. LCD output gets OEM panel delay from ROM headers or static `SiS300_OEMLCDDelay*` tables unless custom PDC exists; TV output gets delay, anti-flicker, phase, and Y-filter from ROM or `SiS300_*` tables. `SetOEMLCDData()` is intentionally compiled out because the data tables are missing.

## State and Persistence Behavior

The main persistent software state is in `struct SiS_Private`. This chunk mutates `SiS_SetFlag` by adding `ProgrammingCRT2`, sets `SiS_SelectCRT2Rate`, updates DDC bus fields (`SiS_DDC_Port`, `SiS_DDC_Index`, `SiS_DDC_Data`, `SiS_DDC_NData`, `SiS_DDC_Clk`, `SiS_DDC_NClk`, `SiS_DDC_DeviceAddr`, `SiS_DDC_ReadAddr`, `SiS_DDC_SecAddr`), and uses `SiS_ChrontelInit` as a cached indication that Chrontel I2C access worked. `SiS_InitDDCRegs()` deliberately clears `SiS_ChrontelInit` to force redetection before ordinary DDC operations.

Hardware state persists in VGA sequencer/CRTC registers, video bridge Part1/Part2/Part4 registers, Chrontel encoder registers, panel controller registers, and bridge enable/lock state. Backlight helpers directly persist bits in Part4 `0x26` for SiS30xLV and Chrontel `0x66` for CH7019. Chrontel power sequencing persists PLL, LVDS, TV path, VSYNC, datapath, and panel power values across mode changes until later mode-setting, blanking, or shutdown code changes them.

PDC and PDCA are treated as durable override values: if set, delay compensation functions write them directly and bypass ROM/table policy. `LVDSHL` similarly overrides Part4 register `0x24` high/low drive settings. Old-ROM `SiS_FinalizeLCD()` can restore backed-up Part1 registers `0x14` through `0x1d` for matching mode numbers, preserving firmware-derived timing when available.

EDID reads persist only in the caller-provided buffer; the DDC helpers restore display gating state after reads but do not preserve all transient bus line states. The I2C stop condition is used to leave the bus idle after successful and most failed paths.

## Dependencies and Integration Points

This code depends on the rest of the SiS mode-setting stack for mode tables, refresh table selection, CRT2 data computation, register group writers, bridge enable/disable, display blanking, retrace waits, and helper predicates such as `SiS_IsYPbPr()`, `SiS_IsChScart()`, `SiS_LCDAEnabled()`, and chipset macros like `IS_SIS650`.

It integrates with hardware through low-level register helpers (`SiS_SetReg`, `SiS_GetReg`, `SiS_SetRegAND`, `SiS_SetRegOR`, `SiS_SetRegANDOR`, `SiS_SetRegSR11ANDOR`) and I/O port bases stored in `SiS_Private` (`SiS_P3c4`, `SiS_P3d4`, `SiS_Part1Port`, `SiS_Part2Port`, `SiS_Part4Port`). It also depends on BIOS ROM access through `VirtualRomBase` and the `SISGETROMW()` macro.

Major data dependencies include Chrontel TV register tables (`SiS_CHTVReg_*`), 315/330/661 delay/filter/phase tables (`SiS310_*`, `SiS_TVPhase`), 300-series OEM delay/filter/phase tables (`SiS300_*`), panel descriptors from `GetLCDStructPtr661_2()`, Barco-specific `barco_p1`, and mode metadata in `SiS_SModeIDTable`, `SiS_EModeIDTable`, `SiS_RefIndex`, and `SiS_VBModeIDTable`.

External integration points are declared in `init301.h` and `sis.h`: the framebuffer driver can call CRT2 setup, DDC, Chrontel register access, SiS30x backlight control, Chrontel 7019 backlight control, and display/bridge helpers. The DDC path provides a private EDID reader rather than using a generic Linux I2C adapter abstraction.

## Risks

- The code programs hardware registers with many chipset, bridge, ROM-layout, panel, and OEM-specific branches. A small condition change can affect only one old laptop/panel combination and be difficult to reproduce.
- Several array indexes are derived from BIOS fields, CR36, mode tables, and panel type values. Incorrect ROM parsing or unexpected panel IDs can index the wrong delay/filter/phase table.
- `SiS_SetCRT2Group()` assumes a precise order: unlock, optionally disable bridge, compute data, write groups, apply OEM/final tweaks, enable bridge, display on, Chrontel mux cleanup, then lock. Reordering can cause visible flicker, bad clocks, or bridge lockout.
- Chrontel I2C operations retry but mostly ignore final failure at higher layers. If encoder writes fail, mode-setting can still continue with stale encoder state.
- Chrontel 700x fallback changes DDC bit mappings only when `SiS_ChrontelInit` is still false. Any stale `SiS_ChrontelInit` state can skip needed bus remapping.
- `SiS_SetCH70xxANDOR()` reads from hardware and writes back without checking for `0xffff` read failure. A failed read can collapse to masked values and write an unintended register value.
- The DDC bit-banging path directly manipulates shared SR11/Part4 DDC bits and temporarily changes SR1F and CR17. Missing restoration or concurrent use would corrupt display or DDC state; this code assumes serialized mode/DDC access.
- `SiS_ReadDDC()` reads 128 or 256 bytes based on DDC type into a caller buffer with no local size check, relying on callers to provide at least 256 bytes.
- `SetSCLKHigh()` has a watchdog for stuck-low clock, but many callers ignore return values from lower-level SCLK helpers inside byte loops. Bus faults may only surface as ACK failures or stale data.
- Old-ROM and OEM comments explicitly note wrong BIOS data and hard-coded vendor values. Replacing tables with "cleaner" ROM-only logic would regress known machines.
- `SetOEMLCDData()` contains disabled, syntactically stale code with missing tables. Enabling it without supplying verified tables would not build and would likely program invalid LCD timings.
- Some helper names such as `DoSomething1/2/3` reflect reverse-engineered behavior. Their register sequences are timing-sensitive power/PLL/datapath operations and should be treated as hardware contracts despite weak names.

## Test and Validation Signals

Useful validation for this chunk includes:

- Build coverage with `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, both enabled, and each disabled, because large parts of the chunk are compile-time gated.
- Mode-set smoke tests for CRT2 LCD, LCDA, VGA2/RAMDAC, TV, SCART, HiVision, YPbPr, Chrontel 7005, and Chrontel 7019 outputs where hardware is available.
- Chrontel register read/write tests that verify the 700x SR11-to-0x0a fallback path, 701x data/clock bit masks, 20-attempt retry behavior, and `SiS_ChrontelInit` caching.
- DDC probe/read tests on CRT1, CRT2 LCD, and CRT2 VGA adapters, including no-monitor, analog EDID on digital port, digital EDID on analog port, and `DDCPortMixup` cases.
- EDID checksum and buffer tests that confirm DDC type 1 reads 128 bytes plus final byte, non-type-1 reads 256 bytes, and invalid all-zero data returns `0xffff`.
- Backlight tests for SiS30xLV Part4 `0x26` and Chrontel 7019 register `0x66`, checking retrace/delay sequencing and no unintended TV/LVDS power changes.
- Panel timing tests for 1024x768, 1280x768, 1280x1024, 1400x1050, 1600x1200, 1680x1050, and custom panels with expansion, no-expansion, VESA timing, and pass-1:1 LCD modes.
- OEM regression tests for named custom systems such as ASUS L3000D, Compaq/Inventec 1280x1024, Clevo 1024/1400 variants, and Barco 1024/1366 paths.
- TV visual tests for NTSC, PAL, PAL-M, PAL-N, NTSC-J, overscan/underscan, 640x480, 800x600, 1024x768, anti-flicker levels, phase increment, edge enhancement, and Y-filter programming.
- Error-path tests with simulated missing ROM pointers, invalid ROM feature bits, unavailable Chrontel ACK, stuck SCLK, and absent bridge flags to confirm functions return or skip programming without corrupting unrelated registers.
