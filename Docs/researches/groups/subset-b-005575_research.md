# subset-b-005575 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.c

## Purpose
`init.c` is the SiS/XGI framebuffer driver's CRT1 mode-initialization engine. It selects BIOS-style mode IDs for CRT, LCD, TV, and secondary VGA outputs; binds the generic `struct SiS_Private` state to the correct 300-series or 315/XGI-series timing tables; unlocks and programs VGA sequencer, CRTC, graphics-controller, attribute-controller, DAC, clock, FIFO, bridge, and chipset-specific registers; optionally clears framebuffer memory; and exposes helper routines for custom CRTC timing conversion.

This file is not Ceph-specific despite living under the `ceph-client` source snapshot. It is Linux fbdev hardware initialization code for `drivers/video/fbdev/sis`.

## Important APIs, types, and functions
The central type is `struct SiS_Private`, defined by the sibling SiS headers. This file mutates its table pointers, register port addresses, chipset flags, detected bridge flags, mode flags, panel geometry, custom-mode timing fields, VRAM pointer/size, and ROM-layout fields.

Public or externally used entry points include:

- `SiSInitPtr()`: selects and installs table pointers for either the SiS 300 family or the SiS 315/XGI family.
- `SiS_GetModeID_LCD()`, `SiS_GetModeID_TV()`, and `SiS_GetModeID_VGA2()`: convert requested geometry/depth/output flags into SiS BIOS mode numbers.
- `SiS_SetReg*()` and `SiS_GetReg*()`: low-level indexed and raw I/O-port access wrappers around `outb/outw/outl` and `inb/inw/inl`.
- `SiS_DisplayOn()` and `SiS_DisplayOff()`: toggle sequencer display blanking.
- `SiSRegInit()`: derives all VGA, bridge, DDC, video-capture, and video-playback I/O port addresses from the device base address.
- `SiSDetermineROMLayout661()`: detects old versus new SiS 661/650 BIOS ROM layouts.
- `SiS_SearchModeID()`, `SiS_GetModeFlag()`, `SiS_GetModePtr()`, `SiS_GetRefCRTVCLK()`, `SiS_GetRefCRT1CRTC()`, `SiS_GetColorDepth()`, and `SiS_GetOffset()`: table lookup helpers used by mode programming and by other init modules.
- `SiS_LoadDAC()`: loads MDA/CGA/EGA/VGA palette data either into CRT1 DAC ports or bridge DAC ports depending on active programming target.
- `SiSSetMode()`: the main mode-set routine called by `sis_main.c`.
- `SiS_CalcCRRegisters()`, `SiS_CalcLCDACRT1Timing()`, and `SiS_Generic_ConvertCRData()`: helpers for custom CRTC timing synthesis and conversion to `fb_var_screeninfo`.

Key internal routines include pointer initializers (`InitCommonPointer()`, `InitTo300Pointer()`, `InitTo310Pointer()`), chipset discovery (`SiS_GetSysFlags()`, `SiSSetLVDSetc()`, `SiS_GetVBType()`), ROM usage selection (`SiSDetermineROMUsage()`), register group writers (`SiS_SetSeqRegs()`, `SiS_SetMiscRegs()`, `SiS_SetCRTCRegs()`, `SiS_SetATTRegs()`, `SiS_SetGRCRegs()`, `SiS_SetCRT1CRTC()`, `SiS_SetCRT1Offset()`, `SiS_SetCRT1VCLK()`, `SiS_SetCRT1ModeRegs()`), FIFO tuning (`SiS_SetCRT1FIFO_300()`, `SiS_SetCRT1FIFO_630()`, `SiS_SetCRT1FIFO_310()`), and final orchestration (`SiS_SetCRT1Group()`).

## Control flow
Mode selection starts with callers supplying either a BIOS mode number or geometry/output flags that are translated by the `SiS_GetModeID*()` helpers. `SiSSetMode()` clears custom-mode state, decides whether framebuffer clearing is required from the high bit of `ModeNo`, normalizes FSTN CRT1 modes, initializes pointers and port addresses, reads system/chipset flags, unlocks sequencer register access, enables PCI/MMIO/2D/3D engine bits, detects LVDS/Chrontel/Trumpion/Conexant possibilities, decides whether ROM data is usable, and unlocks CRT2 registers.

For normal modes, `SiSSetMode()` resolves `ModeNo` into a standard or extended table index with `SiS_SearchModeID()`. It then detects video bridge type, initializes bridge programming clock state, gathers connector/output information through sibling bridge helpers, derives TV and LCD information, runs low-mode tests, and rejects the mode if required memory exceeds `VideoMemorySize`.

The CRT1 path runs when the mode is for CRT1, simultaneous scan, or LCDA. `SiS_SetCRT1Group()` selects the standard VGA register template, disables the bridge if low-mode safety requires it, resets segment registers, writes the sequencer, miscellaneous output, CRTC, attribute, and graphics-controller groups, clears extended sequencer registers, resets VCLK when bridge/LVDS hardware needs it, finds the refresh-rate table row, and then applies sync polarity, extended CRTC timing, pitch/offset, pixel clock, FIFO thresholds, and mode-specific control bits. It loads the DAC, clears VRAM when requested, waits for retrace where appropriate, and turns display output on.

The CRT2 path is delegated to `SiS_SetCRT2Group()` from companion bridge code when simultaneous scan, CRT2-only, or LCDA output is selected and a supported bridge/LVDS/TV encoder exists. After both paths, `SiSSetMode()` re-enables CRT1 gating, applies odd capture/video register workarounds, restores selected bridge/CRTC backup bits, adjusts SIS760 AGP/UMA/LFB timing, conditionally relocks sequencer access, and returns success.

The custom timing helpers operate after timing fields such as `CHTotal`, `CHDisplay`, `CVTotal`, and `CVDisplay` are already loaded into `struct SiS_Private`. `SiS_CalcCRRegisters()` encodes those values into the `CCRT1CRTC[]` register image; `SiS_CalcLCDACRT1Timing()` derives scaled LCD CRT1 timings from panel geometry and writes them to hardware; `SiS_Generic_ConvertCRData()` decodes CRTC bytes back into framebuffer margins and sync lengths.

## State and persistence behavior
There is no filesystem or durable software persistence. State persists in three places only:

- `struct SiS_Private`: table pointers, port addresses, mode flags, bridge flags, panel data, ROM-layout metadata, custom timing data, and cached backup register values for one driver instance.
- VGA/bridge/chipset registers: mode programming writes persist in hardware until another mode set, reset, suspend/resume sequence, or device removal.
- VRAM: `SiS_ClearBuffer()` clears all or part of framebuffer memory depending on mode class when `SiS_flag_clearbuffer` is set.

`SiSDetermineROMUsage()` reads `VirtualRomBase` and sets `SiS_UseROM`, `SiS_ROMNew`, `SiS_EMIOffset`, `SiS_PWDOffset`, and `SiS661LCD2TableSize`, but it does not modify ROM contents. Low-level register helpers are immediate side-effect APIs and assume the caller already serialized access at the driver level.

## Dependencies and integration points
The file depends on Linux I/O primitives from `<asm/io.h>`, framebuffer structures from `<linux/fb.h>`, local type and table definitions from `init.h`, `initdef.h`, `vgatypes.h`, `vstruct.h`, `sis.h`, and `sisfb.h`, and generated/large timing tables from `300vtbl.h` and `310vtbl.h` under `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`.

It integrates with `sis_main.c`, which calls `SiSSetMode()` for normal mode changes and fallback/default modes, and with `initextlfb.c`, which uses `SiSInitPtr()` while querying linear framebuffer and mode details. It calls sibling bridge and chipset helpers such as `SiS_GetVBInfo()`, `SiS_SetYPbPr()`, `SiS_SetTVMode()`, `SiS_GetLCDResInfo()`, `SiS_SetCRT2Group()`, `SiS_DisableBridge()`, `SiS_UnLockCRT2()`, `SiS_WaitRetrace1()`, `SiS_IsDualEdge()`, `SiS_IsVAMode()`, `SiS_GetVCLK2Ptr()`, `SiS_GetRatePtr()`, `SiS_GetCH700x()`, and PCI config helpers such as `sisfb_read_nbridge_pci_dword()`.

Compile-time integration is heavily gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`. A build with only one family enabled will reject unsupported chip families through `SiSInitPtr()`.

## Risks and edge cases
The main risk is direct hardware programming. Incorrect table data, chip detection, bridge detection, or register ordering can blank the screen, corrupt timings, or leave CRT2/LCDA state inconsistent. Many branches encode empirical legacy hardware behavior for specific chip revisions, ROM layouts, TV standards, and panel types; changes need real hardware coverage or very careful table-level comparison.

Mode ID helpers index depth-specific arrays directly, so callers must supply the expected small depth index rather than raw bits per pixel. `SiSSetMode()` has early failure paths after unlocking sequencer registers or before restoring all state; callers must treat a false return as a partially touched hardware state. Register access wrappers have no locking, range checking, or I/O failure reporting.

ROM parsing assumes enough valid bytes behind `VirtualRomBase` once `UseROM` is true. New-layout detection reads fixed offsets and version characters and can misclassify malformed ROMs. FIFO and clock routines perform integer arithmetic with mode and memory clocks; invalid clocks or custom timings can produce unsafe thresholds. The code also contains disabled or TODO paths for XGI dual-chip setup, SiS340 details, and Conexant support, which means apparent detection does not always imply full programming support.

## Test signals
Useful build signals are successful compilation with `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, both enabled, and each family disabled where supported by Kconfig. Static checks should flag missing prototypes, impossible enum values, and array-index assumptions for mode depth.

Runtime validation needs hardware or emulation capable of SiS/XGI VGA I/O. High-value tests include setting standard VGA modes and extended modes through `sis_main.c`, verifying `SiSSetMode()` return values and visual output, checking fallback 640x480 initialization, exercising CRT-only, CRT2-only, simultaneous scan, LCDA, LCD, TV, and VGA2 paths, and confirming memory-size rejection for modes that exceed configured VRAM. Custom-mode tests should compare `SiS_CalcCRRegisters()` and `SiS_Generic_ConvertCRData()` against known timing values. Regression signals include unchanged register traces for representative chip/mode pairs, expected framebuffer clearing behavior, stable palette output, and no blank display after suspend/resume or repeated mode switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.h

## Purpose
`init.h` is the private data header consumed by `init.c` and the surrounding SiS framebuffer initialization modules. It includes the local SiS type contracts and Linux kernel interfaces, then defines static lookup tables for BIOS mode IDs, VGA DAC palettes, standard VGA register templates, TV timing data, LCD scaling/timing data, LVDS timing data, and CRT1 timing images used for slave/LVDS modes.

The header is table-heavy rather than API-heavy. Its main purpose is to provide the immutable data that `SiSInitPtr()` installs into `struct SiS_Private`, allowing shared init code to choose mode programming values without hard-coding every timing in the control-flow logic.

## Important APIs, types, and data
The header guard is `_INIT_H_`. It includes `initdef.h`, `vgatypes.h`, `vstruct.h`, Linux `types`, `io`, and `fb` headers, `sis.h`, and `<video/sisfb.h>`. It also undefines `SIS_CP` before including Linux headers, matching the legacy shared-code environment this driver came from.

The most important data groups are:

- `ModeIndex_*` arrays: map supported resolutions to four depth-indexed BIOS mode numbers. Examples include 320x200, 640x480, 800x600, 1024x768, 1280x1024, widescreen modes such as 1280x720/800/854 and 1680x1050, and high modes such as 1920x1440 or 2048x1536.
- `SiS_MDA_DAC`, `SiS_CGA_DAC`, `SiS_EGA_DAC`, and `SiS_VGA_DAC`: palette source data loaded by `SiS_LoadDAC()`.
- `SiS_SModeIDTable`, `SiS_StResInfo`, and `SiS_ModeResInfo`: standard-mode metadata and resolution metadata used by mode lookup and memory/depth calculations.
- `SiS_StandTable`: standard VGA register templates containing sequencer, CRTC, attribute, graphics-controller, miscellaneous, and related values for text, MDA/CGA/EGA/VGA, and extended placeholder modes.
- `SiS_SoftSetting` and `SiS_OutputSelect`: default soft straps used through pointers in `struct SiS_Private`.
- TV timing/data tables such as `SiS_NTSCTiming`, `SiS_PALTiming`, `SiS_HiTV*Timing`, `SiS_HiTVGroup3*`, `SiS_StPALData`, `SiS_ExtPALData`, `SiS_StNTSCData`, `SiS_ExtNTSCData`, `SiS_StHiTVData`, `SiS_St2HiTVData`, `SiS_ExtHiTVData`, `SiS_St525pData`, `SiS_St750pData`, and `SiS_Ext750pData`.
- LCD data tables such as `SiS_LCD1280x720Data`, `SiS_StLCD1280x768_2Data`, `SiS_ExtLCD1280x768_2Data`, `SiS_LCD1280x800Data`, `SiS_LCD1280x800_2Data`, `SiS_LCD1280x854Data`, `SiS_LCD1280x960Data`, `SiS_StLCD1400x1050Data`, `SiS_ExtLCD1400x1050Data`, `SiS_LCD1680x1050Data`, `SiS_StLCD1600x1200Data`, `SiS_ExtLCD1600x1200Data`, and `SiS_NoScaleData`.
- LVDS/Chrontel timing tables such as `SiS_LVDS320x240Data_*`, `SiS_LVDS640x480Data_1`, `SiS_LVDS800x600Data_1`, `SiS_LVDS1024x600Data_1`, `SiS_LVDS1024x768Data_1`, `SiS_CHTVUNTSCData`, `SiS_CHTVONTSCData`, and `SiS_LVDSCRT1Data` arrays for CRT1 slave timings.

The concrete struct layouts for these tables, such as `struct SiS_St`, `struct SiS_StandTable_S`, `struct SiS_TVData`, `struct SiS_LCDData`, `struct SiS_LVDSData`, and `struct SiS_LVDSCRT1Data`, come from the included local headers.

## Control flow
The header itself has no executable runtime control flow, but it strongly shapes the control flow in `init.c`. `SiS_GetModeID*()` selects entries from `ModeIndex_*` arrays according to geometry, depth index, VGA engine family, panel type, TV standard, and bridge flags. `SiS_SearchModeID()` scans `SiS_SModeIDTable` or the family-specific extended mode table installed from `300vtbl.h` or `310vtbl.h`. `SiS_GetModePtr()` chooses a `SiS_StandTable` row, and the register group writers in `init.c` stream that row into hardware.

`InitCommonPointer()` binds many of this header's common TV/LCD/LVDS tables into the private state, while `InitTo300Pointer()` and `InitTo310Pointer()` add family-specific tables from other headers. Later bridge and panel routines follow those pointers rather than referencing the static arrays directly.

## State and persistence behavior
All definitions in this header are `static const` lookup data. They do not persist state and are not mutated by normal execution. Persistence occurs only when `init.c` copies pointers to these arrays into `struct SiS_Private` or writes values derived from them into hardware registers. Because the arrays have internal linkage, every translation unit that includes this header gets its own private copy, which is acceptable for this legacy driver but means the header is not a lightweight declaration-only interface.

Preprocessor blocks keep some experimental or unused timing variants compiled out with `#if 0`, preserving historical data without making it active. Compile-time options around `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315` limit parts of the standard table region but most data remains visible to the including translation unit.

## Dependencies and integration points
`init.h` is tightly integrated with `init.c`; it is not a public kernel API. It depends on local SiS mode flag constants, panel identifiers, bridge flags, and table struct definitions from `initdef.h`, `vgatypes.h`, `vstruct.h`, and `sis.h`. It also needs Linux I/O and framebuffer definitions because this shared init layer mixes data declarations with routines and structures that use kernel I/O and `struct fb_var_screeninfo`.

The mode ID arrays and timing tables integrate with the rest of the driver through fields in `struct SiS_Private`, especially the table pointers assigned by `SiSInitPtr()`. The bridge code consumes the TV/LCD/LVDS table pointers when programming CRT2, panel scaling, and TV encoder timings. The DAC arrays integrate only through `SiS_LoadDAC()`.

## Risks and edge cases
The biggest risk is table correctness. Many values are hardware magic numbers with comments documenting board-specific, BIOS-version-specific, or empirically chosen behavior. A one-byte timing change can affect sync polarity, blanking, scaling, panel centering, FIFO behavior, or display visibility.

The `ModeIndex_*` arrays assume the depth selector passed by callers is a valid 0..3 index. Unsupported combinations are represented by `0x00`, so callers must treat zero as no mode. Several high-resolution modes are restricted by engine family or bridge capability in `init.c`, not by the arrays themselves.

Because this header defines large `static const` arrays, including it from multiple C files can duplicate read-only data and create subtle divergence if one translation unit is built under different preprocessor options. The file also carries disabled alternative data with non-English comments and TODO notes; re-enabling those blocks without hardware validation would be risky.

## Test signals
Validation should focus on consumers. Build tests should compile the SiS framebuffer driver with each relevant configuration and catch type/layout mismatches between this header and the struct definitions in included headers. Table integrity checks can verify sentinel entries such as `0xff` terminators, depth-array lengths, nonzero mode IDs for advertised supported modes, and expected row counts for panel tables consumed by bridge code.

Runtime signals include successful mode lookup for common resolutions and depth indices, correct palette output for MDA/CGA/EGA/VGA modes, stable standard-register traces for legacy modes, correct LCD centering/scaling for each panel table, and TV output matching NTSC/PAL/HiTV/YPbPr expectations. Any change to these tables should be tested on representative 300-series, 315-series, LVDS, SiS30x bridge, Chrontel, and XGI hardware paths when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.h -->
