# Research: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005576`: lines 1-8162, `Docs/researches/chunks/subset-b-005576_research.md`
- `subset-b-005577`: lines 8163-11379, `Docs/researches/chunks/subset-b-005577_research.md`

## Chunk Research

### subset-b-005576: lines 1-8162

# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.c lines 1-8162

## Scope and purpose

This chunk is the first major portion of `init301.c`, the SiS/XGI CRT2/video-bridge initialization implementation used by the Linux `sisfb` driver. It covers the data tables and helper logic needed to derive CRT2 state for SiS 300/315-era chips, LCD panels, SiS 30x video bridges, LVDS transmitters, Chrontel TV encoders, and YPbPr/HiVision TV modes. The code is deeply hardware-facing: most functions translate `struct SiS_Private` mode/chip/bridge state into direct indexed register writes through `SiS_SetReg*()` and direct reads through `SiS_GetReg*()`.

The covered range does not include the final top-level `SiS_SetCRT2Group()` body, but it defines most of the functions that top-level path uses later in the file: bridge detection and enable/disable, rate and VCLK selection, TV/LCD mode classification, CRT2 timing-data collection, and the Part1-Part5 register programming groups.

## Static data and compile-time gates

The top of the chunk enables optional behavior with local macros:

- `SET_EMI` writes EMI tuning registers for 302LV/ELV panels.
- `SET_PWD` writes PWD values for 301/302LV panels.
- `COMPAL_HACK`, `COMPAQ_HACK`, and `ASUS_HACK` preserve machine-specific EMI overrides.

The file is gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`, so many functions compile only for the relevant engine family. It includes `init301.h` plus `oem300.h` or `oem310.h`, making this chunk depend on the shared mode tables, bridge flags, chip IDs, panel constants, and OEM-specific lookup tables stored in `struct SiS_Private`.

Important local tables include:

- `SiS_YPbPrTable[3][64]`: Part2 TV timing tables for YPbPr 525i, 525p, and 750p.
- `SiS_TVPhase[]`: subcarrier/phase bytes for NTSC, PAL, PAL-M/N, special 1024, and newer 30xBLV phases.
- `SiS_HiTVGroup3_1` and `_2`: Part3 register programming blocks for progressive YPbPr/HiTV modes.
- `SiS_Part2CLVX_*`: 315-only 4-tap scaler coefficient tables for 301C/302ELV style bridges, selected by TV mode and source/destination dimensions.
- `SiS_LCDStruct661[]`: fallback LCD panel timing rows for 661-era chips when BIOS tables are absent or unreliable.
- `SiS300_TrumpionData`: 300-series Trumpion LVDS programming blocks.

These tables are persistent static constants except `SiS300_TrumpionData`, which is static writable data but treated as a fallback table. The hardware-visible state lives in registers and in mutable fields inside `struct SiS_Private`.

## Public APIs visible in this chunk

The chunk defines several functions exported through `init301.h` or `sis.h`:

- `SiS_GetRatePtr()`: selects a refresh-rate table index for the requested mode and current CRT2 target.
- `SiS_WaitRetrace1()`: waits for VGA retrace with watchdog loops.
- `SiS_IsDualEdge()` and `SiS_IsVAMode()`: query CR38/bridge mode state for dual-edge and LCDA/VA output.
- `SiS_GetVBInfo()`: builds `SiS_Pr->SiS_VBInfo` from bridge presence, CR30/CR31/CR38/CR35 state, driver mode, and requested display target.
- `SiS_SetYPbPr()` and `SiS_SetTVMode()`: derive `SiS_Pr->SiS_YPbPr` and `SiS_Pr->SiS_TVMode`.
- `SiS_GetLCDResInfo()`: derives panel size/type/scaling/timing flags and stores `PanelXRes`, `PanelYRes`, `PanelHT`, `PanelVT`, sync offsets, VCLK indices, and `SiS_LCDInfo`.
- `SiS_GetVCLK2Ptr()` and `SiS_GetResInfo()`: resolve CRT2 clock and resolution-table indices.
- `SiS_DisableBridge()`: powers down or gates CRT2/bridge paths before programming.
- `SiS_DDC2Delay()`: delay helper used by DDC and panel sequencing.
- `SiS_SetChrontelGPIO()` for 300/SIS630: manipulates ACPI GPIO backing Chrontel output selection.

The chunk also defines major private helpers later invoked by `SiS_SetCRT2Group()` outside this range:

- `SiS_GetCRT2Data()`, `SiS_GetCRT2Data301()`, and `SiS_GetCRT2DataLVDS()`
- `SiS_SetCRT2ModeRegs()`
- `SiS_EnableBridge()`
- `SiS_SetGroup1()`, `SiS_SetGroup2()`, `SiS_SetGroup2_C_ELV()`, `SiS_SetGroup3()`, `SiS_SetGroup4()`, `SiS_SetGroup4_C_ELV()`, `SiS_SetGroup5()`
- `SiS_ModCRT1CRTC()`, `SiS_SetCRT2ECLK()`, and the beginning of `SiS_SetCHTVReg()`

## Control flow

The intended mode-set flow, inferred from later references in this file and from `init.c`, is:

1. The caller determines `ModeNo`/`ModeIdIndex` and invokes `SiS_GetVBInfo()`.
2. `SiS_SetYPbPr()`, `SiS_SetTVMode()`, and `SiS_GetLCDResInfo()` populate TV/panel flags in `SiS_Private`.
3. `SiS_GetRatePtr()` selects a refresh-rate entry compatible with the current CRT2 target, using `SiS_AdjustCRT2Rate()` to reject unsupported CRT2 variants.
4. The top-level CRT2 path disables the bridge through `SiS_DisableBridge()` when needed.
5. `SiS_SetCRT2ModeRegs()` sets mode-type and output-enable register bits.
6. `SiS_GetCRT2Data()` computes the active CRT2 timing state, selecting the LVDS path, 301/30x bridge path, LCD tables, TV tables, custom-mode fields, or RAMDAC2-derived CRT1 timings.
7. Group programming functions write register groups:
   - Part1: CRT2 CRTC, FIFO, panel-link timing, LVDS scaling.
   - Part2: TV encoder or LCD panel timings, TV phase, scaler coefficients, center/scale offsets.
   - Part3: TV filter and HiTV/YPbPr data.
   - Part4: bridge VCLK, overflow, line-buffer, dual-link, EMI/PWD, and special CLV/ELV settings.
   - Part5: DAC load for VGA-like non-slave paths.
8. `SiS_ModCRT1CRTC()` may rewrite CRT1 CRTC registers when slave mode requires CRT1 to match LVDS/TV constraints.
9. `SiS_SetCRT2ECLK()` programs sequencer clock registers for CRT2 engine clocks.
10. `SiS_EnableBridge()` powers CRT2/bridge/panel/backlight paths back on with hardware-specific delays and retrace waits.

## Mode and state derivation

`SiS_GetVBInfo()` is the central state-normalization function. It reads CR30/CR31, and on 315-era chips also CR35/CR38, to classify the requested output into `SetCRT2ToLCD`, `SetCRT2ToLCDA`, `SetCRT2ToRAMDAC`, `SetCRT2ToSVIDEO`, `SetCRT2ToAVIDEO`, `SetCRT2ToSCART`, `SetCRT2ToHiVision`, or `SetCRT2ToYPbPr525750`. It clears impossible combinations, folds non-driver mode into simulation/slave behavior, and disables CRT2 when no supported output bit survives. It also enforces low-color restrictions for LVDS/Chrontel and 301BDH LCD paths.

`SiS_SetYPbPr()` maps older HiVision/CR38 encoding to internal YPbPr flags, while `SiS_SetTVMode()` turns bridge and BIOS state into flags such as PAL, PAL-M, PAL-N, NTSC-J, overscan, 525i/525p/750p, HiVision, simulated TV, aspect ratio, and RPLL divisor behavior. This state later selects timing tables, phase bytes, VCLKs, and Part2/Part3 programming.

`SiS_GetLCDResInfo()` is the LCD state hub. It decodes CR36 and newer CR39/BIOS structures into `SiS_LCDResInfo` and `SiS_LCDTypeInfo`, then writes panel dimensions, totals, sync offsets, panel clock indices, scaling policy, dual-link, RGB18, pass-1:1, VESA timing, and LVDS DDA flags. It also handles many hardware exceptions: 661 LCD structure rows, ROM-provided panel timing, custom EDID/preferred panel modes, 301/315 translation quirks, Barco/custom panels, 848/856 panels, Trumpion, DSTN/FSTN, and OEM-specific scaling restrictions.

## Timing and clock selection

`SiS_GetRatePtr()` reads the requested refresh index from CR33 and walks the refresh table for the mode. It clamps or rewrites the index for LCD/LCDA/Chrontel TV cases, uses `LCDRefreshIndex[]` to limit LCD refreshes by panel type, and calls `SiS_AdjustCRT2Rate()` to find an entry whose `Ext_InfoFlag` supports the current CRT2 target.

`SiS_GetVCLK2Ptr()` chooses a CRT2 clock index from mode tables, panel timing, TV mode, Chrontel TV tables, or VGA2/RAMDAC paths. It has special mappings for pass-1:1 LCD modes whose generic CRT VCLK index does not match the bridge VCLK table, and it overrides clocks for YPbPr/HiVision/TV divisor modes.

`SiS_GetCRT2ResInfo()`, `SiS_GetCRT2Ptr()`, `SiS_GetRAMDAC2DATA()`, `SiS_CalcPanelLinkTiming()`, `SiS_GetCRT2DataLVDS()`, and `SiS_GetCRT2Data301()` combine mode-resolution data, panel native timings, TV timing tables, no-scale tables, ROM LCD mode data, and custom-mode timing fields into the common runtime fields:

- `SiS_HDE`, `SiS_VDE`, `SiS_HT`, `SiS_VT`
- `SiS_VGAHDE`, `SiS_VGAVDE`, `SiS_VGAHT`, `SiS_VGAVT`
- `SiS_RVBHCMAX`, `SiS_RVBHCFACT`, `SiS_RVBHRS`, `SiS_RVBHRS2`
- TV flicker and Y filter coefficients
- panel display-end skew values via `SiS_GetLVDSDesData()`

Those fields are later consumed almost verbatim by the Part1-Part4 register writers, so arithmetic mistakes here become direct display timing failures.

## Register programming groups

`SiS_SetCRT2ModeRegs()` initializes core bridge mode bits in Part1 and Part4 registers. It distinguishes LCDA, slave mode, RAMDAC2, LCD, TV, 301 vs 30xB/LV/C, LVDS, dual-edge, dual-link, 301BDH, and 740/661-era quirks. It also contains long comments around 315+301DH color handling and explicitly programs registers that can affect TV color correctness.

`SiS_SetGroup1()` programs the Part1 CRT2 CRTC path. It sets offset/pitch, FIFO thresholds (`SiS_SetCRT2FIFO_300()` or `_310()`), horizontal/vertical totals and retrace, delay compensation, and then dispatches to `SiS_SetGroup1_LVDS()` or `SiS_SetGroup1_301()` when the bridge is in slave/panel-link mode. `SiS_SetGroup1_LVDS()` computes panel-link display start/end, sync starts/ends, vertical and horizontal scaling factors, LVDS DDA bits, Part4 scaler mirrors, Trumpion blocks, and DSTN/FSTN memory-window registers. `SiS_SetGroup1_301()` synthesizes CRT-like timings into `CCRT1CRTC` and copies translated CRTC fields into Part1 for slave mode.

`SiS_SetGroup2()` programs Part2 TV/LCD encoder state. For TV it selects timing and phase data, writes timing register ranges, adjusts vertical centering, writes TV output selection bits, handles YPbPr/HiVision/progressive variants, and programs bridge-specific horizontal scaling. For LCD it writes panel active, blanking, retrace, centering, and bridge offsets, with optional table-driven overrides through `SiS_GetCRT2Part2Ptr()`, `SiS_Group2LCDSpecial()`, and `SiS_Set300Part2Regs()`. `SiS_SetGroup2_C_ELV()` writes 4-tap scaler coefficient tables for capable 301C/302ELV-style bridges.

`SiS_SetGroup3()` writes Part3 TV filter defaults and full HiTV/YPbPr tables. It is bypassed for LCDA and can be customized by `SIS_CP` compile hooks.

`SiS_SetGroup4()` writes Part4 bridge data: horizontal/vertical counters, scaling factors, line-buffer limits, decimation mode, bridge VCLK through `SiS_SetCRT2VCLK()`, dual-link/EMI setup through `SiS_SetDualLinkEtc()`, and special progressive TV/YPbPr settings through `SiS_SetGroup4_C_ELV()`. The Part4 logic is highly sensitive to `VB_SIS30xBLV`, `VB_SIS30xCLV`, `VB_SIS302LV`, dual-link, half-DCLK, and TV mode flags.

`SiS_SetGroup5()` is small: it reloads DAC data for ModeVGA when CRT2 is not in slave/load-DAC mode and LCDA is not active.

## Bridge power sequencing

`SiS_DisableBridge()` and `SiS_EnableBridge()` are large hardware sequencing routines. They do not trust mode-set local variables because comments state they may be called outside the mode-switch context. Instead they read live CR and Part register state, then branch on bridge family, chip family, LVDS/Chrontel, dual-edge/VA, LCD-vs-TV state, and custom panel IDs.

The sequence includes:

- gating bridge processor bits in Part2 and Part1;
- toggling SR11/SR1E/SR32 and display on/off;
- calling `SiS_PanelDelay()`, `SiS_PanelDelayLoop()`, `SiS_VBLongWait()`, and retrace waits around power transitions;
- controlling LVDS panel/backlight bits in Part4 registers 0x26/0x27/0x30/0x34;
- applying PWD values via `SiS_HandlePWD()`;
- applying EMI values from ROM, cached probe fields, or machine-specific fallbacks;
- invoking Chrontel backlight/power helpers for CH701x paths.

The code preserves temporary SR06 state around some 315 LVDS transitions and uses long delay loops for panels that require additional power-stabilization time.

## Chrontel integration visible in this chunk

The chunk declares and calls Chrontel-specific helpers (`SiS_Chrontel701xOn/Off`, `SiS_ChrontelInitTVVSync()`, `SiS_ChrontelDoSomething1()`, `SiS_Chrontel701xBLOn/BLOff()`, `SiS_SetCH700x()`, `SiS_SetCH701x()`, `SiS_SetCH70xxANDOR()`). `SiS_SetCHTVReg()` starts at the end of this chunk and maps TV mode plus overscan/PAL-M/PAL-N state to Chrontel register data tables. The covered portion fully shows CH7005 setup for 300-era paths, including mode limits, PAL/NTSC black-level and bandwidth setup, FSCI/loop-filter handling, and macrovision-looking register accesses. The CH7019 branch begins but continues beyond the chunk boundary.

## Dependencies and integration points

This code depends on:

- `struct SiS_Private` as the shared state object and table repository.
- Register helpers declared elsewhere: `SiS_SetReg()`, `SiS_SetRegAND()`, `SiS_SetRegOR()`, `SiS_SetRegANDOR()`, `SiS_GetReg()`, `SiS_GetRegByte()`, `SiS_SetRegByte()`, `SiS_SetRegShort()`, `SiS_GetRegShort()`.
- Mode helpers from `init.c`/other SiS init files: `SiS_SearchModeID()`, `SiS_GetModeFlag()`, `SiS_GetModePtr()`, `SiS_GetColorDepth()`, `SiS_GetOffset()`, `SiS_LoadDAC()`, `SiS_CalcLCDACRT1Timing()`, `SiS_CalcCRRegisters()`, `SiS_GetRefCRTVCLK()`, `SiS_GetRefCRT1CRTC()`.
- 300-series memory/FIFO helpers and PCI config reads: `SiS_GetFIFOThresholdIndex300()`, `SiS_GetFIFOThresholdB300()`, `SiS_GetLatencyFactor630()`, `sisfb_read_nbridge_pci_dword()`, `sisfb_read_lpc_pci_dword()`.
- BIOS ROM macros such as `SISGETROMW()` and `VirtualRomBase` offsets for LCD and OEM panel data.
- Hardware flags and constants from `initdef.h`, `vgatypes.h`, `vstruct.h`, `sis.h`, and `sisfb.h`.

The mode-init path in `init.c` calls the public state derivation functions before programming CRT2. Later lines in this same file call the private group functions from `SiS_SetCRT2Group()`.

## State and persistence behavior

The code mutates three categories of state:

- `struct SiS_Private` runtime fields: `SiS_VBInfo`, `SiS_TVMode`, `SiS_YPbPr`, `SiS_LCDInfo`, `SiS_LCDResInfo`, `SiS_LCDTypeInfo`, panel geometry/timings, VCLK indices, scaling flags, EMI/PWD caches, CRTC calculation buffers, and CRT2 timing values.
- Hardware registers: sequencer/CRTC registers and bridge Part1-Part4/Part2/Part3 ports are directly written. These changes persist in device hardware until another mode set, power transition, or driver reset changes them.
- BIOS-derived cached decisions: panel timings, EMI values, PWD values, and ROM mode-data pointers are read from `VirtualRomBase` and copied into runtime fields or registers.

There is no heap allocation or file-level dynamic persistence in this chunk. Persistence is hardware state plus the long-lived `SiS_Private` object shared across the driver.

## Risks and fragile areas

- Register programming is highly branch-dependent and stateful. Calling helpers out of the expected order can use stale `SiS_Private` timing fields and write invalid bridge timings.
- Many calculations use `unsigned short` truncation and manual overflow packing. Large custom timings or unsupported panel dimensions can wrap or underflow.
- Several code paths intentionally emulate BIOS quirks or machine-specific hacks. Removing or normalizing them risks regressions on old laptop panels.
- Delay loops are busy-wait based and depend on port reads. Incorrect delay ordering can cause panel power sequencing, backlight, or bridge PLL failures.
- `SiS_GetVGAHT2()` divides by derived vertical blank products; invalid `SiS_RVBHCMAX`, `SiS_RVBHCFACT`, `SiS_VT`, or `SiS_VDE` state could produce division by zero.
- BIOS ROM offsets are trusted after coarse checks. Bad or mismatched ROM data can program bogus panel timings, EMI, PWD, and VCLK values.
- Custom mode handling relies on many `CP_*`, `CH*`, `CV*`, and `CSR*` fields being prevalidated elsewhere.
- Chrontel and SiS bridge register maps differ; several branches write similar-looking registers with different meanings.
- Conditional compilation can hide unused or untested combinations, so changes must be checked under both `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`.

## Test and validation signals

Useful validation points for this chunk are mostly hardware or register-state oriented:

- Build-test with both 300 and 315 support enabled to catch preprocessor-specific breakage.
- Exercise mode sets for CRT2 LCD, LCDA, VGA2/RAMDAC2, S-Video, composite, SCART, HiVision, YPbPr 525i/525p/750p, and Chrontel TV where hardware is available.
- Compare Part1-Part4 register dumps before and after changes for representative panels: 1024x768, 1280x1024, 1400x1050, 1600x1200, 1280x800/854, custom EDID panel, dual-link panel, DSTN/FSTN, and Trumpion.
- Verify panel power sequencing by checking display/backlight transitions across disable/enable, suspend/resume-like paths, and mode switches from TV to LCD.
- Validate TV output visually and through encoder register dumps for PAL, NTSC, PAL-M, PAL-N, NTSC-J, overscan, simulated TV, and 1024-wide special modes.
- For custom modes, assert that `SiS_GetCRT2Data*()`, `SiS_SetGroup1*()`, `SiS_SetGroup2()`, and `SiS_SetCRT2ECLK()` receive prevalidated totals/syncs and do not produce register values outside hardware field widths.

## Chunk boundary notes

The requested chunk stops at line 8162 inside `SiS_SetCHTVReg()`. The Chrontel 7019 programming branch and the final top-level CRT2 orchestration continue after this chunk. Later chunk research should connect this section’s helper implementations to the complete `SiS_SetCRT2Group()` sequence and the DDC/CH70xx helper bodies that follow.

### subset-b-005577: lines 8163-11379

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
