# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/300vtbl.h

## Purpose
`300vtbl.h` is a static register and timing table catalog for the SiS 300-series framebuffer initialization code. It supplies mode IDs, reference timing indices, CRTC register values, memory/video clocks, sequencer defaults, LCD/LVDS/CRT2 bridge tables, Chrontel TV encoder tables, and panel-specific timing descriptors for chips such as SiS 300/305/540/630/730.

## Important APIs, types, and functions
The header defines data, not functions. Major table families are `SiS300_EModeIDTable`, `SiS300_RefIndex`, `SiS300_VBModeIDTable`, `SiS300_CRT1Table`, `SiS300_MCLKData_630`, `SiS300_MCLKData_300`, mutable `SiS300_VCLKData`, `SiS300_SR15`, `SiS300_PanelDelayTbl`, LCD timing tables for 1024x768 and 1280x1024, `SiS300_CRT2Part2_1024x768_*`, BARCO and 848x480 LVDS data, Chrontel PAL/NTSC/SVIDEO overscan data, `SiS300_PanelType04_*`, Chrontel slave CRTC tables, Chrontel register tables, and Chrontel VCLK selector arrays. The structures are declared in the SiS init headers and referenced through pointers in `struct SiS_Private`.

## Control flow
There is no direct control flow in the header. `init.c` includes it under `CONFIG_FB_SIS_300`; `InitTo300Pointer()` assigns these arrays into `SiS_Pr` function-state pointers after chip detection. Later mode-setting code indexes the tables by BIOS-like mode IDs, reference indices, panel type, TV standard, bridge type, and chip type to program CRT1, CRT2, memory clocks, video clocks, LCD scaling, LVDS timing, and TV encoder registers.

## State and persistence
Most arrays are `static const` and are effectively immutable build-time state embedded in the driver. `SiS300_VCLKData` is non-const, matching the broader SiS init code's expectation that VCLK tables can be patched or treated through mutable pointers. No runtime persistence exists beyond the in-memory driver image and the hardware registers programmed from these values.

## Dependencies and integration points
The header depends on structure definitions and constants from `init.h`, `initdef.h`, `vstruct.h`, and related SiS headers. It is tightly integrated with `init.c` pointer initialization and `init301.c` CRT2/LVDS/TV programming. Build inclusion is gated by `CONFIG_FB_SIS_300`, while `drivers/video/fbdev/sis/Makefile` links the common SiS init objects into `sisfb.o` when `CONFIG_FB_SIS` is enabled.

## Risks and test signals
Risks are table-index drift, sentinel mistakes, incorrect chip-family selection, mode IDs that disagree with shared `ModeIndex_*` arrays, mutable VCLK data assumptions, and hard-to-review numeric register regressions. Several entries encode legacy or panel-specific quirks, so small numeric changes can break only one output path. Test signals include compile coverage with `CONFIG_FB_SIS_300`, mode-set tests across 8/16/32 bpp, CRT1-only and CRT2 clone modes, LVDS panels including BARCO/848x480 cases, Chrontel NTSC/PAL/SVIDEO variants, suspend/resume mode restore, and comparing programmed registers against known-good hardware or BIOS traces.
