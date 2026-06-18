# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/310vtbl.h

## Purpose
`310vtbl.h` is the static register and timing table catalog for the SiS 315/330/340-era and related XGI framebuffer initialization path. It extends the 300-series table model with newer modes, more chip-specific memory-clock tables, separate bridge VCLK data, LVDS panel delays, widescreen modes, and PAL-M/PAL-N Chrontel TV variants.

## Important APIs, types, and functions
The header defines data arrays only. Key tables include `SiS310_EModeIDTable`, `SiS310_RefIndex`, `SiS310_CRT1Table`, chip-specific `SiS310_MCLKData_0_*` tables for 315/650/330/660/760/761/340, `SiS310_MCLKData_1*` ECLK data, mutable `SiS310_VCLKData`, mutable `SiS310_VBVCLKData`, `SiS310_SR15`, standard and LVDS panel delay tables, LCD timing data, `SiS310_CRT2Part2_1024x768_1`, multiple Chrontel overscan data tables, Chrontel slave CRTC tables, Chrontel register tables for NTSC/PAL/PAL-M/PAL-N, and Chrontel VCLK selector arrays. The mode table covers legacy VGA resolutions plus newer widescreen modes such as 1280x800, 1680x1050, 1920x1080, and 960-wide panel modes.

## Control flow
The header has no executable path. `init.c` includes it under `CONFIG_FB_SIS_315`; `InitTo310Pointer()` selects tables based on `SiS_Pr->ChipType`, assigning the proper memory-clock table for 315, 550/650/740, 330, 661/741, 760, 761, or 340/XGI-class hardware. Subsequent mode setup indexes these arrays through `struct SiS_Private` pointers to program CRT1 timings, RAM clocks, dot clocks, bridge clocks, LVDS delays, LCD scaling, and TV encoder registers.

## State and persistence
The file contributes static driver data. Most tables are `static const`; `SiS310_VCLKData` and `SiS310_VBVCLKData` are mutable arrays because the SiS init code treats clock tables as runtime-adjustable data. The values persist only as part of the loaded driver and as programmed hardware register state after a mode set.

## Dependencies and integration points
The file depends on SiS structure definitions from the init headers and is coupled to pointer fields in `struct SiS_Private`. It integrates with `init.c` for chip-family pointer binding and with `init301.c` for bridge, LVDS, LCD, and Chrontel TV programming. Its availability is controlled by `CONFIG_FB_SIS_315`; the common `sisfb.o` link target includes the consuming init objects.

## Risks and test signals
Risks include selecting the wrong memory-clock table for a chip variant, breaking sentinel-terminated lookups, VCLK/VBVCLK mismatch for bridge modes, incorrect widescreen reference indices, stale comments around known Chrontel register inaccuracies, and regressions limited to PAL-M/PAL-N or LVDS paths. Test signals include `CONFIG_FB_SIS_315` build coverage, mode setting on each supported chip family when available, CRT1 and CRT2 output combinations, bridge-clock validation, widescreen and high-resolution modes, LVDS delay behavior, PAL/NTSC/PAL-M/PAL-N TV output, and register comparison against known-good tables.
