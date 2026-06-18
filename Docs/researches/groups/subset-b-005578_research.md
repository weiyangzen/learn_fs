# subset-b-005578 Research

Grouped research for the SiS fbdev bridge, OEM data, mode-timing, and 2D acceleration files listed in subset-b-005578. Each source file section is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.h

## Purpose

`init301.h` is the bridge-initialization interface for SiS 30x-series external display hardware. It is consumed by `init301.c` and `sis_main.c` to expose CRT2, LCD, TV encoder, DDC, and bridge power-control routines while sharing the global mode and hardware definitions from `initdef.h`, `vstruct.h`, and `sis.h`.

## Important APIs, Types, And Functions

- Declares CRT2/bridge control APIs: `SiS_UnLockCRT2`, `SiS_EnableCRT2`, `SiS_DisableBridge`, `SiS_SetCRT2Group`, `SiS_SiS30xBLOn`, and `SiS_SiS30xBLOff`.
- Declares mode-selection helpers: `SiS_GetRatePtr`, `SiS_GetVBInfo`, `SiS_SetTVMode`, `SiS_SetYPbPr`, `SiS_GetLCDResInfo`, `SiS_GetVCLK2Ptr`, and `SiS_GetResInfo`.
- Declares output-specific helpers for Chrontel encoders: `SiS_SetCH700x`, `SiS_GetCH700x`, `SiS_SetCH701x`, `SiS_GetCH701x`, and `SiS_SetCH70xxANDOR`, with extra 315-series backlight helpers under `CONFIG_FB_SIS_315`.
- Declares DDC helpers: `SiS_DDC2Delay`, `SiS_ReadDDC1Bit`, and `SiS_HandleDDC`.
- Re-declares cross-file init routines implemented in `init.c`, including mode table search, CRT register conversion, DAC loading, FIFO-threshold helpers, and PCI bridge reads.

## Control Flow

This header has no executable control flow. It creates compile-time linkage between `init301.c` and the generic init/fbdev layers. Runtime flow generally starts in `sis_main.c`, which calls mode selection and bridge setup functions; those functions use the prototypes here to coordinate generic mode table lookup, bridge-specific programming, TV/LCD register setup, and DDC reads.

## State And Persistence

The APIs operate on `struct SiS_Private *SiS_Pr`, which carries mode tables, hardware port addresses, chip type, bridge flags, ROM data, and per-mode state. Persistent state is hardware state written to VGA sequencer/CRTC ports, bridge part registers, Chrontel encoder registers, panel/TV flags, and backlight state. The header itself stores no data.

## Dependencies And Integration Points

- Includes `initdef.h`, `vgatypes.h`, `vstruct.h`, `sis.h`, and `<video/sisfb.h>`.
- Depends on Linux fbdev and I/O headers for types and port/MMIO access.
- Feature sections are gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`.
- Integrates with `init301.c` for implementation, `init.c` for shared mode logic, and `sis_main.c` for fbdev-facing mode setting and DDC operations.

## Risks

- Prototype duplication with `sis.h` and `init.h` can drift if function signatures change.
- Most functions mutate low-level display hardware through `SiS_Pr`; incorrect flags or mode indexes can blank displays, select the wrong encoder, or misprogram TV/LCD timings.
- Conditional declarations mean build coverage must include both 300 and 315 configurations to catch missing prototypes.

## Test Signals

- Build with `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, and combined configurations to validate conditional prototypes.
- Exercise CRT2 enable/disable, TV/LCD switching, and DDC through fbdev mode setting paths.
- Check for warnings about missing prototypes or incompatible pointer types when compiling `init301.c`, `init.c`, and `sis_main.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initdef.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initextlfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initextlfb.c

## Purpose

`initextlfb.c` provides Linux fbdev-specific helpers that convert SiS internal mode table data into framebuffer timing values. It is the bridge between the driver core's mode numbers/rate indexes and `struct fb_var_screeninfo` fields used by fbdev validation and reporting.

## Important APIs, Types, And Functions

- `sisfb_mode_rate_to_dclock(struct SiS_Private *SiS_Pr, unsigned char modeno, unsigned char rateindex)`: returns the pixel clock in Hz for a SiS mode/rate pair, defaulting to 65 MHz when initialization or lookup fails.
- `sisfb_mode_rate_to_ddata(struct SiS_Private *SiS_Pr, unsigned char modeno, unsigned char rateindex, struct fb_var_screeninfo *var)`: fills timing and sync fields in `var` using CRT1 timing data and returns success as `1` or failure as `0`.
- `sisfb_gettotalfrommode(struct SiS_Private *SiS_Pr, unsigned char modeno, int *htotal, int *vtotal, unsigned char rateindex)`: extracts total horizontal and vertical scan counts from CRT register table bytes.
- External dependencies include `SiSInitPtr`, `SiS_SearchModeID`, and `SiS_Generic_ConvertCRData`.

## Control Flow

Each function initializes the private table pointers with `SiSInitPtr`, normalizes fbdev-style `rateindex` by decrementing nonzero values, maps special 315 modes `0x5a` and `0x5b` to base mode IDs, and then uses `SiS_SearchModeID`. The selected mode's reference table index (`RRTI`) chooses normal, wide, or rate-offset timing entries. `sisfb_mode_rate_to_ddata` converts CRT register data into fbdev margins/syncs and then applies sync polarity, interlace, and double-scan flags. `sisfb_gettotalfrommode` reconstructs totals from packed CRTC bytes and doubles vertical total for interlaced modes.

## State And Persistence

The file is read-only with respect to hardware. It reads `SiS_Pr` tables such as `SiS_EModeIDTable`, `SiS_RefIndex`, `SiS_VCLKData`, and `SiS_CRT1Table`, and writes only caller-provided output objects (`fb_var_screeninfo`, `htotal`, and `vtotal`). No persistent state is stored by these helpers.

## Dependencies And Integration Points

- Included by the SiS fbdev build and declared in `sis.h`.
- Called by `sis_main.c` during var setup, mode validation, and display information reporting.
- Depends on `HaveWideTiming`, `InterlaceMode`, `DoubleScanMode`, `FB_SYNC_*`, and `FB_VMODE_*` constants.
- The mode/rate table shapes are defined in `vstruct.h` and populated by the init table machinery.

## Risks

- Rate indexes are not range-checked after adding to `RRTI`; callers must supply valid indexes for the mode.
- Wide-screen modes ignore refresh-rate selection when `SiS_UseWide == 1`, which is intentional but can surprise callers expecting exact rate control.
- The fallback 65 MHz clock can hide lookup failures unless the caller logs or validates separately.
- Packed CRTC extraction depends on table layout and byte positions; table format changes require synchronized updates.

## Test Signals

- For known mode/rate pairs, compare returned pixel clocks and totals against the SiS reference tables.
- Validate 315 aliases `0x5a` and `0x5b`, wide timing paths, interlaced modes, and double-scan modes.
- Exercise `sis_main.c` mode-setting paths and confirm `fb_var_screeninfo` sync polarity and `vmode` values match expected modelines.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/initextlfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem300.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem300.h

## Purpose

`oem300.h` contains built-in OEM calibration tables for SiS 300-series bridge programming. These constants supply fallback LCD delay, TV delay, flicker, phase, Y-filter, and custom Barco projector register values used when BIOS-provided OEM data is unavailable, disabled, or known through driver-specific handling.

## Important APIs, Types, And Functions

This file defines only `static const` data:

- TV and LCD delay tables: `SiS300_OEMTVDelay301`, `SiS300_OEMTVDelayLVDS`, `SiS300_OEMTVFlicker`, `SiS300_OEMLCDDelay2`, `SiS300_OEMLCDDelay3`, `SiS300_OEMLCDDelay4`, and `SiS300_OEMLCDDelay5`.
- TV phase tables: `SiS300_Phase1` and `SiS300_Phase2`.
- TV Y-filter tables: `SiS300_Filter1` and `SiS300_Filter2`.
- Custom Barco iQ Pro R300 table: `barco_p1`, containing part-1 register programming triplets.

## Control Flow

No code executes in this header. `init301.c` includes it under `CONFIG_FB_SIS_300` and selects arrays based on bridge type, panel type, TV standard, mode index, and custom hardware detection. The call sites program values into bridge part registers, especially Part2 for TV timing/filtering and Part1 for Barco-specific output setup.

## State And Persistence

The tables are immutable in kernel memory. Their values become persistent hardware state only after `init301.c` writes selected entries to SiS bridge registers. They do not track runtime state; selection state is carried in `SiS_Pr` and hardware flags defined in `initdef.h`.

## Dependencies And Integration Points

- Included by `init301.c`.
- Indexed using panel, TV, and mode constants from `initdef.h`.
- Integrates with bridge register accessors such as `SiS_SetReg` in the 300-series CRT2 path.
- Complements BIOS/OEM table offset constants in `initdef.h`; built-in tables are a fallback or override for ROM data.

## Risks

- Table dimensions and index meanings are implicit; an incorrect index can select a plausible but wrong timing value.
- Many rows are repeated default values, so accidental offset mistakes may only appear on specific panels or TV standards.
- Custom Barco register programming is hardware-specific and can be risky if applied to the wrong subsystem or mode.
- There are no compile-time assertions tying dimensions to selector ranges in `init301.c`.

## Test Signals

- Exercise 300-series LCD and TV output modes with SiS 301/301B/302B/LVDS bridges, with and without BIOS OEM tables.
- Verify Part1/Part2 register traces for NTSC, PAL, HiVision, flicker, phase, and Y-filter programming against known-good hardware.
- Confirm Barco-specific paths only trigger for the intended custom panel/projector combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem310.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem310.h

## Purpose

`oem310.h` contains built-in OEM calibration and custom timing data for SiS 315/330/340-era chips and related 650/651/740/LVDS bridge combinations. It provides LCD delay compensation, TV delay/anti-flicker/edge/filter/phase tables, and two custom panel timing tables used by `init301.c`.

## Important APIs, Types, And Functions

This file defines only `static const` data:

- LCD delay compensation arrays for bridge/chip combinations: `SiS310_LCDDelayCompensation_301`, `SiS310_LCDDelayCompensation_650301LV`, `SiS310_LCDDelayCompensation_651301LV`, `SiS310_LCDDelayCompensation_651302LV`, `SiS310_LCDDelayCompensation_3xx301B`, and `SiS310_LCDDelayCompensation_3xx301LV`.
- TV delay arrays: `SiS310_TVDelayCompensation_301`, `SiS310_TVDelayCompensation_301B`, `SiS310_TVDelayCompensation_740301B`, `SiS310_TVDelayCompensation_651301LV`, `SiS310_TVDelayCompensation_651302LV`, and `SiS310_TVDelayCompensation_LVDS`.
- TV image adjustment tables: `SiS310_TVAntiFlick1`, `SiS310_TVEdge1`, `SiS310_TVYFilter1`, `SiS310_TVYFilter2`, `SiS310_TVPhaseIncr1`, and `SiS310_TVPhaseIncr2`.
- Disabled `#if 0` 661 TV delay arrays document unused data.
- Custom timing/register tables: `SiS310_ExtCompaq1280x1024Data` and `SiS310_CRT2Part2_Asus1024x768_3`.

## Control Flow

There is no executable control flow here. `init301.c` includes this file for 315-series builds and selects table entries in CRT2 setup based on chip family, bridge type, panel index, TV standard, mode timing, and custom panel IDs. Selected values are written to bridge Part2 registers or used as LCD timing descriptors.

## State And Persistence

The arrays are immutable driver data. Runtime persistence occurs when chosen entries are applied to bridge registers or used to calculate LCD timings. The selection state comes from `SiS_Pr`, BIOS/custom panel detection, `VB_*` flags, and panel IDs.

## Dependencies And Integration Points

- Included by `init301.c` when `CONFIG_FB_SIS_315` is enabled.
- Uses `struct SiS_LCDData` and `struct SiS_Part2PortTbl` from `vstruct.h`.
- Coupled to `init301.c` call sites around LCD/TV delay compensation, TV filter programming, phase increment programming, custom Compaq timing selection, and Asus Part2 register setup.

## Risks

- Comments mark some values as guessed or known wrong but retained for documentation; using the wrong array for a bridge can degrade signal quality or panel behavior.
- Compact flattened LCD delay arrays rely on selector arithmetic, not named structs.
- The disabled 661 TV delay data can mislead future changes if re-enabled without hardware validation.
- Custom timing arrays are narrow workarounds and must not leak into generic mode paths.

## Test Signals

- Build and boot with `CONFIG_FB_SIS_315`, covering 301, 301B, 301LV, 302LV, LVDS, 740, 650/651, and M650 paths where possible.
- Trace register writes in `init301.c` for TV anti-flicker, edge, Y-filter, and phase programming.
- Validate custom Compaq 1280x1024 and Asus 1024x768 panel paths against their expected panel IDs and modelines.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/oem310.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis.h

## Purpose

`sis.h` is the central Linux fbdev private header for the SiS framebuffer driver. It defines driver versioning, device IDs, accelerator IDs, capability flags, hardware register addresses, MMIO helpers, video bridge flags, LCD command enums, VRAM heap structures, the large `struct sis_video_info` driver state object, and cross-file function prototypes.

## Important APIs, Types, And Functions

- Version and debug helpers: `VER_MAJOR`, `VER_MINOR`, `VER_LEVEL`, `DPRINTK`, `TWDEBUG`, and `SISFAIL`.
- PCI and fb acceleration identifiers for SiS and XGI devices.
- Capability and resource sizing constants for cursor memory, command queues, turbo queues, and offscreen heap allocation.
- VGA/bridge register offsets and aliases such as `SISSR`, `SISCR`, `SISPART1` through `SISPART5`, and `SISDAC2*`.
- Video bridge masks `VB_*` and `VB2_*`, including bridge type groups for TMDS, LVDS, YPbPr, HiVision, LCDA, scaler, and RAMDAC capability checks.
- I/O helpers: `SiS_SetReg*`, `SiS_GetReg*`, and MMIO macros `MMIO_IN*`/`MMIO_OUT*`.
- Enums: `_SIS_LCD_TYPE` for panel classes and `_SIS_CMDTYPE` for command queue modes.
- Heap structures: `SIS_OH`, `SIS_OHALLOC`, and `SIS_HEAP`.
- Driver state: `struct sis_video_info`, the fbdev `par` object holding `SiS_Private`, fbdev state, PCI devices, memory mappings, mode/current timing state, acceleration state, bridge flags, panel/TV state, hardware cursor state, and linked-list membership.
- Prototypes for init, mode lookup, CRT2, DDC, acceleration, PCI access, and SiS-specific memory ioctls.

## Control Flow

The header itself has no runtime flow. It enables the rest of the driver to share a common state object and helper API. `sis_main.c` owns most top-level fbdev control flow and uses this header to call init, mode, bridge, acceleration, heap, and register helpers. `sis_accel.c` uses the MMIO macros and `struct sis_video_info` acceleration fields. `init.c` and `init301.c` use the same register and bridge definitions for hardware programming.

## State And Persistence

`struct sis_video_info` is the persistent per-device state for the driver. It stores mapped framebuffer/MMIO bases, BIOS pointer, memory sizes, mode geometry, current timings, command queue length and type, acceleration enablement, video bridge flags, panel and TV settings, detected devices, cursor memory, user/module parameters, and registration status. Hardware persistence is represented by VGA sequencer/CRTC registers, bridge part registers, command queues, and framebuffer memory written through the helpers.

## Dependencies And Integration Points

- Includes `<video/sisfb.h>`, `vgatypes.h`, and `vstruct.h`.
- Used by nearly every driver file, including `sis_main.c`, `sis_accel.c`, `init.c`, and `init301.c`.
- Integrates with Linux PCI, fbdev, I/O memory, spinlock, and compatibility APIs.
- Serves as the common declaration point for fbdev callbacks implemented in `sis_accel.c` and mode helpers implemented in `initextlfb.c`.

## Risks

- The `struct sis_video_info` layout is broad and highly coupled; changes can affect probe, mode setting, acceleration, cursor, heap, and ioctl paths.
- Many bit masks mirror hardware register layouts, and several `VB_*` and `VB2_*` groups overlap by design.
- MMIO helpers are thin wrappers around raw reads/writes; callers must provide valid mapped bases and offsets.
- Conditional prototypes can hide missing implementations unless all config families are built.

## Test Signals

- Full driver builds across 300 and 315 configurations, including XGI paths where available.
- Probe/remove tests that map MMIO/framebuffer, initialize `struct sis_video_info`, set fb ops, and clean up resources.
- Mode-switch, DDC, CRT2, acceleration, cursor, ypan, and ioctl tests to cover the major state fields.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.c

## Purpose

`sis_accel.c` implements the fbdev 2D acceleration hooks for SiS 300 and 315/310-series engines. It accelerates solid rectangle fills, screen-to-screen copies, and synchronization by translating fbdev operations into SiS MMIO command sequences defined in `sis_accel.h`, while falling back to generic `cfb_*` helpers when acceleration is unavailable.

## Important APIs, Types, And Functions

- ROP lookup tables: `sisALUConv` for source/destination ROPs, `sisPatALUConv` for pattern-as-source ROPs, and `myrops` to map fbdev fill ROPs.
- 300-series internal routines under `CONFIG_FB_SIS_300`: `SiS300Sync`, `SiS300SetupForScreenToScreenCopy`, `SiS300SubsequentScreenToScreenCopy`, `SiS300SetupForSolidFill`, and `SiS300SubsequentSolidFillRect`.
- 315-series routines under `CONFIG_FB_SIS_315`: `SiS310Sync`, `SiS310SetupForScreenToScreenCopy`, `SiS310SubsequentScreenToScreenCopy`, `SiS310SetupForSolidFill`, and `SiS310SubsequentSolidFillRect`.
- Exported/internal entry points: `sisfb_initaccel`, `sisfb_syncaccel`, `fbcon_sis_sync`, `fbcon_sis_fillrect`, and `fbcon_sis_copyarea`.

## Control Flow

`fbcon_sis_fillrect` and `fbcon_sis_copyarea` first reject inactive fbdev state, disabled acceleration, bad engine state, zero-size operations, and out-of-bounds rectangles. They clip dimensions to virtual resolution, derive color or copy direction, choose the 300 or 315 path from `ivideo->sisvga_engine`, program setup registers, trigger the command, and finally call `sisfb_syncaccel`. The 300 copy path computes explicit X/Y direction flags. The 315 copy path relies on hardware direction detection but adjusts source and destination base addresses together when overlapping areas exceed the 2048-line coordinate range.

## State And Persistence

The functions mutate `struct sis_video_info` acceleration fields such as `CommandReg` and `cmdqueuelength`, read geometry and color state from `fb_info`, and write persistent hardware command/register state through MMIO. They do not allocate memory. `sisfb_initaccel` initializes the optional acceleration spinlock only when `SISFB_USE_SPINLOCKS` is enabled.

## Dependencies And Integration Points

- Includes Linux module/kernel/fb/io headers plus `sis.h` and `sis_accel.h`.
- Registered through `sis_main.c` fb ops as `fb_fillrect`, `fb_copyarea`, and sync callback.
- Falls back to `cfb_fillrect` and `cfb_copyarea` when acceleration is disabled or engine status is bad.
- Depends on `ivideo->DstColor`, `video_linelength`, `video_offset`, `SiS310_AccelDepth`, `mmio_vbase`, `cmdqueuelength`, and `engineok` set up elsewhere.

## Risks

- Busy-wait sync macros can hang if hardware never reports idle.
- Coordinate/base adjustments for large virtual screens are hardware-specific and easy to regress, especially around overlapping blits.
- Spinlock protection is compiled out by default; concurrent framebuffer operations rely on higher-level serialization or hardware tolerance.
- ROP indexes assume caller-provided fbdev ROP values stay in range.

## Test Signals

- Compare accelerated and `cfb_*` fallback output for fills and overlapping copies at 8, 16, and 32 bpp.
- Test virtual y resolutions above 2048 to cover base-address compensation.
- Exercise both 300 and 315 paths with acceleration enabled/disabled and engineok true/false.
- Use stress tests for console scrolling and rectangle fills while checking for hangs in `sisfb_syncaccel`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.h

## Purpose

`sis_accel.h` defines the MMIO register map, command flags, synchronization macros, command queue accounting, and public prototypes for the SiS fbdev 2D acceleration engine. It is paired with `sis_accel.c` and abstracts the differences between the older 300 engine register layout and the 315/310 layout.

## Important APIs, Types, And Functions

- Optional critical-section macros: `CRITBEGIN`, `CRITEND`, and `CRITFLAGS`, controlled by `SISFB_USE_SPINLOCKS`.
- Command constants for blit, color expansion, lines, trapezoid fill, transparent blit, alpha/3D/Z/gradient commands, source selectors, pattern flags, 300-series direction flags, clipping, transparency, and color expansion subfunctions.
- 315 register addresses such as `SRC_ADDR`, `SRC_PITCH`, `DST_ADDR`, `DST_PITCH`, `RECT_WIDTH`, `RECT_HEIGHT`, `PAT_FGCOLOR`, `COMMAND_READY`, and `FIRE_TRIGGER`.
- 300 register helper address macros `BR(x)` and `PBR(x)`.
- Idle macros `SiS300Idle` and `SiS310Idle`.
- Setup/fire macros for source/destination base, pitch, coordinates, rectangle size, colors, transparency keys, mono patterns, clipping, ROP, command flags, and command dispatch for both 300 and 310 engines.
- Function prototypes for `sisfb_initaccel`, `sisfb_syncaccel`, `fbcon_sis_sync`, `fbcon_sis_fillrect`, and `fbcon_sis_copyarea`.

## Control Flow

The macros implement inline command sequencing. Each setup macro checks `CmdQueLen`, calls the relevant idle macro when the queue is exhausted, writes one or more MMIO registers, and decrements `CmdQueLen`. `SiS300DoCMD` writes the command and trigger through the 300 register block; `SiS310DoCMD` writes `COMMAND_READY` and `FIRE_TRIGGER`. Idle macros poll status registers multiple times before resetting queue accounting.

## State And Persistence

The macros mutate `ivideo->cmdqueuelength` through `CmdQueLen`, update `ivideo->CommandReg`, and write MMIO registers under `ivideo->mmio_vbase`. Hardware command queue state persists in the graphics engine until commands complete. Optional spinlocks protect register sequences only if the header-level feature flag is enabled.

## Dependencies And Integration Points

- Requires `struct sis_video_info` and MMIO macros from `sis.h`.
- Used directly by `sis_accel.c`.
- Uses `Q_STATUS` from `sis.h` for 315 idle polling.
- Exposes fbdev acceleration hooks consumed by `sis.h` and registered by `sis_main.c`.

## Risks

- Macros evaluate arguments directly and have statement-like side effects, so callers must avoid expressions with side effects.
- Busy-wait loops have no timeout and can wedge the caller if MMIO status is invalid or hardware is hung.
- Queue length accounting is manual and must match the number of MMIO writes per macro.
- Without spinlocks, interleaved callers could corrupt command sequences if higher-level fbdev locking is insufficient.

## Test Signals

- Compile with and without `SISFB_USE_SPINLOCKS` to validate macro declarations.
- Run accelerated fills/copies while instrumenting MMIO writes to ensure queue decrement and idle refresh behavior matches expected command counts.
- Force small command queue lengths to exercise idle paths.
- Compare 300 and 315 register sequences for equivalent fill/copy operations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_accel.h -->
