# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initdef.h

## Purpose

`initdef.h` centralizes the symbolic constants used by SiS mode initialization and SiS 30x bridge programming. It maps chip families, bridge capabilities, display-output flags, panel identifiers, timing table indexes, BIOS layout offsets, and OEM table sizes into named constants shared by `init.c`, `init301.c`, and Linux-specific fbdev glue.

## Important APIs, Types, And Functions

This file defines no functions or types. Its important exported symbols are macro groups:

- Chip predicates such as `IS_SIS330`, `IS_SIS650740660`, and `IS_SIS661741660760`.
- Bridge type masks such as `VB_SIS301`, `VB_SIS30xB`, `VB_SISLVDS`, `VB_SISYPBPR`, `VB_SISPART4SCALER`, and `VB_SISPOWER`.
- Mode and output flags such as `SetCRT2ToLCD`, `SetCRT2ToTV`, `SetCRT2ToRAMDAC`, `DriverMode`, `HotKeySwitch`, `CRT2Mode`, `HaveWideTiming`, `DoubleScanMode`, `InterlaceMode`, and sync polarity masks.
- TV mode flags for PAL, NTSC-J, PAL-M/N, YPbPr 525i/525p/750p, HiVision, aspect ratios, overscan, and simulation modes.
- Panel IDs for 300, 310, and 661-era hardware plus unified `Panel_*` values used by higher-level panel logic.
- Resolution-table indexes `SIS_RI_*` and VCLK indexes for 300/315 video-clock tables.
- BIOS/OEM table offsets and sizes, including CRT2 pointer data, LVDS data, TV filter/phase/delay tables, mode entry field positions, and old 315-series ROM offsets.

## Control Flow

No runtime code executes in this file. Runtime control flow in `init.c` and `init301.c` branches heavily on these macros: chip predicates select per-family paths; `VB_*`, `SetCRT2To*`, and `TVSet*` masks select output programming; panel constants index LCD timing tables; BIOS offsets locate ROM-resident data or decide whether to use built-in defaults.

## State And Persistence

The macros describe both in-memory state fields and hardware/ROM state:

- `SiS_Pr->ChipType`, `SiS_Pr->SiS_SysFlags`, `SiS_Pr->SiS_VBType`, and mode/TV/panel fields are interpreted through these masks.
- CR/SR register bit definitions mirror persistent hardware state read from or written to VGA/bridge registers.
- BIOS offsets define persistent ROM data layout used to seed tables and OEM behavior.

## Dependencies And Integration Points

- Included by `init.h`, `init301.h`, and `initextlfb.c`.
- Used directly by `init.c` and `init301.c`, including the OEM table programming paths.
- Its comments document register layouts for CR32, CR35, CR37, CR38, CR39, CR79, CR7C, and CR7E, which are essential integration points with the video BIOS and hardware bridge.

## Risks

- Many constants are ABI-like contracts with BIOS tables and hardware registers; changing values can silently corrupt mode selection.
- Several masks reuse bit positions depending on chip family or context, such as CR38 and `SetCRT2ToLCDA`/`HotKeySwitch`, so consumers must apply the correct family checks.
- Table indexes such as panel IDs and VCLK IDs must stay aligned with data arrays in other files.
- Expressions like `0x04 - 0x30` intentionally encode relative I/O offsets; casual cleanup could break port calculations.

## Test Signals

- Compile all supported config combinations to catch macro drift in conditional paths.
- Validate representative CRT1, CRT2, LCD, TV, LCDA, YPbPr, and dual-link modes on 300, 315, 650/740, and 661+ paths.
- Compare BIOS-derived table offsets against known ROM images and ensure fallback built-in tables produce equivalent register programming.
