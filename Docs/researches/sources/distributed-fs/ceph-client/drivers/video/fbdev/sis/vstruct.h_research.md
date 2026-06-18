# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vstruct.h

## Purpose
`vstruct.h` defines the shared data structures used by the SiS/XGI universal mode-setting code. It contains compact hardware timing table record types and the large `struct SiS_Private`, which is the low-level mode engine's working context embedded inside `struct sis_video_info`.

## Important APIs And Types
- Timing table records: `SiS_PanelDelayTbl`, `SiS_LCDData`, `SiS_TVData`, `SiS_LVDSData`, `SiS_LVDSDes`, `SiS_LVDSCRT1Data`, `SiS_CHTVRegData`, `SiS_St`, `SiS_VBMode`, `SiS_StandTable_S`, `SiS_Ext`, `SiS_Ext2`, `SiS_Part2PortTbl`, `SiS_CRT1Table`, `SiS_MCLKData`, `SiS_VCLKData`, `SiS_VBVCLKData`, `SiS_StResInfo_S`, and `SiS_ModeResInfo_S`.
- Custom timing constants `CUT_NONE` through `CUT_PANEL856` are stable numeric IDs used by `sis_main.h` and low-level mode tables. The comment explicitly says not to change them for `sisfb` compatibility.
- `struct SiS_Private` holds chip identity, ROM pointers, VRAM/IO addresses, bridge feature flags, mode flags, panel/TV/LVDS/Chrontel timing state, table pointers, custom mode data, backup register values, panel scaler choices, PDC/EMI data, DDC state, and parsed custom panel timing data.

## Control Flow And Use
- `sisfb_probe()` initializes key `SiS_Private` fields: chip type/revision, `ivideo` back-pointer, ROM pointer/use flags, IO addresses through `SiSRegInit()`, panel scaler, custom timing, PDC/PDCA, SR/CR quirks, and VRAM address/size.
- Low-level functions such as `SiSSetMode()`, `SiS_GetModeID_LCD()`, `SiS_GetModeID_TV()`, `SiS_GetModeID_VGA2()`, `SiS_HandleDDC()`, bridge setup, and timing conversion routines read and write this structure during mode detection and programming.
- `sis_main.c` updates selected fields after detection: `SiS_CustomT`, `PanelSelfDetected`, `DDCPortMixup`, `SiS_UseLCDA`, `HaveEMI`, `HaveEMILCD`, `PDC`, `PDCA`, `UsePanelScaler`, and TV/LCD flags.

## State And Persistence Behavior
- `struct SiS_Private` is embedded per card and persists as long as the framebuffer device exists.
- It caches both static capabilities and mutable runtime state. Examples include ROM layout flags, DDC bits, current TV/LCD mode flags, panel dimensions, custom mode timings, register backups, and pointers to generation-specific timing tables.
- Table pointer fields point to static timing data supplied by other source files, while `VirtualRomBase` points to a `vmalloc()` copy owned and freed by `sis_main.c`.
- `VideoMemoryAddress` is an `__iomem` pointer adjusted during probe to the console viewport offset; `VideoMemorySize` is later set to the driver-visible framebuffer size, not necessarily total VRAM.

## Dependencies And Integration Points
- Depends on `vgatypes.h` for `SISIOMEMTYPE` and `SISIOADDRESS`.
- Consumed by `sis.h`, `sis_main.h`, `sis_main.c`, and the low-level mode-setting implementation files.
- Its table record shapes must match static timing arrays in the SiS init code and the expectations of bridge/LVDS/TV setup routines.
- The back-pointer `ivideo` lets low-level code call back into PCI helper functions and access driver context indirectly.

## Risks And Edge Cases
- `struct SiS_Private` is very broad and mixes configuration, hardware-derived state, mutable mode state, and table pointers; partial initialization can cause low-level mode-setting code to read stale or default values.
- Many fields are small integer register mirrors. Width/sign mistakes can silently corrupt hardware programming.
- The custom timing constants are compatibility-sensitive; changing values would break boot parameters, autodetection tables, and possibly userspace expectations surfaced through `sisfb_info`.
- `VideoMemoryAddress` and IO address fields require correct `__iomem` handling; treating them as normal memory can bypass required accessors.
- Custom panel arrays have fixed length 7. Any parser/filler in related code must avoid exceeding those arrays.

## Test Signals
- Build and sparse checks should validate `__iomem` use for `VideoMemoryAddress` and IO access.
- Mode-setting tests should cover CRT1, LCD, TV, LVDS, Chrontel, custom timing, panel scaler, and DDC paths because all mutate `SiS_Private`.
- Regression checks should compare expected register programming before/after edits to timing record layouts or `SiS_Private` fields.
- Special timing options and autodetected quirk IDs should be verified to map to the intended `CUT_*` values.
