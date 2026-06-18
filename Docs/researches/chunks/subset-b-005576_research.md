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
