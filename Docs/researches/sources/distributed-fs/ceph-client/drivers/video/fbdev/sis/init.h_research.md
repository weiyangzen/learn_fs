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
