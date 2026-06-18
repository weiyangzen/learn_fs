# Research: subset-b-005579

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.c

## Purpose
`sis_main.c` is the main Linux fbdev PCI driver for SiS 300/540/630/730, SiS 315/55x/65x/66x/74x/330/76x/34x, and XGI V3XT/V5/V8/Z7 display chips. It binds PCI devices, maps framebuffer/MMIO resources, optionally POSTs uninitialized cards, detects display bridges and attached outputs, chooses a startup video mode, registers a `struct fb_info`, implements fbdev callbacks, exposes SiS private ioctls, and owns the driver's offscreen VRAM heap.

The file is not filesystem code despite the repository path. It is a hardware driver with persistent state in PCI config space, VGA/bridge registers, VRAM, `struct sis_video_info`, global boot/module parameters, and the legacy global `sisfb_heap`.

## Important APIs And Functions
- PCI/module entry points: `sisfb_init()`, `sisfb_init_module()`, `sisfb_remove_module()`, `sisfb_probe()`, `sisfb_remove()`, and `sisfb_driver`.
- fbdev operations in `sisfb_ops`: `sisfb_check_var`, `sisfb_set_par`, `sisfb_pan_display`, `sisfb_blank`, `sisfb_setcolreg`, `sisfb_ioctl`, accelerated `fb_fillrect`/`fb_copyarea`, `cfb_imageblit`, mmap/read/write helpers, and `fbcon_sis_sync`.
- Mode selection: `sisfb_search_mode()`, `sisfb_search_vesamode()`, `sisfb_search_refresh_rate()`, `sisfb_validate_mode()`, `sisfb_do_set_var()`, `sisfb_set_mode()`, `sisfb_pre_setmode()`, `sisfb_post_setmode()`, `sisfb_reset_mode()`.
- Display and monitor detection: `sisfb_get_VB_type()`, `sisfb_detect_VB_connect()`, `sisfb_sense_crt1()`, `SiS_SenseLCD()`, `SiS_Sense30x()`, `SiS_SenseCh()`, `sisfb_handle_ddc()`, `sisfb_interpret_edid()`, `sisfb_detect_lcd_type()`, `sisfb_detect_custom_timing()`, `sisfb_save_pdc_emi()`.
- Hardware/POST helpers: `sisfb_find_rom()`, `sisfb_check_rom()`, `sisfb_post_sis300()`, `sisfb_post_xgi()`, `sisfb_post_xgi_ramsize()`, DDR/DDR2 setup helpers, `sisfb_get_dram_size()`, and `sisfb_post_map_vram()`.
- VRAM heap: `sisfb_heap_init()`, `sisfb_poh_allocate()`, `sisfb_poh_free()`, `sis_malloc()`, `sis_free()`, with per-card heap metadata plus a first-card global heap pointer for old DRM/DRI users.
- Bridge/blanking helpers: `sisfb_myblank()`, `sisfb_setupvbblankflags()`, `sisfb_CheckVBRetrace()`, `sisfb_set_TVxposoffset()`, `sisfb_set_TVyposoffset()`, `sisfb_handle_command()`.
- Callback exports to init code: `sisfb_read_nbridge_pci_dword()`, `sisfb_write_nbridge_pci_dword()`, `sisfb_read_lpc_pci_dword()`, `sisfb_write_nbridge_pci_byte()`, and `sisfb_read_mio_pci_word()` are used by `init.c`/`init301.c` through `struct SiS_Private`.

## Control Flow
1. Boot/module parameters are reset by `sisfb_setdefaultparms()` and parsed either from `fb_get_options("sisfb", ...)` for built-in use or from `module_param()` values in `sisfb_init_module()`.
2. `sisfb_init()` aborts if fb modesetting is disabled, then registers `sisfb_driver`.
3. `sisfb_probe()` allocates `fb_info` plus `sis_video_info`, records PCI IDs/subsystem data, handles northbridge/LPC companion devices, initializes `SiS_Pr`, copies global parameter choices into per-card fields, enables the PCI device if needed, derives MMIO/VRAM bases, and unlocks VGA registers.
4. Probe optionally finds and copies a video ROM, detects custom timing quirks, identifies XGI Z9 versus Z7, and POSTs uninitialized hardware only for supported SiS300/XGI cases.
5. Probe determines VRAM size, reserves and maps framebuffer/MMIO regions, initializes command queue/cursor memory layout, builds the offscreen heap, detects CRT1/video bridge/LCD/TV/monitor details, selects a valid default mode, builds `fb_var_screeninfo`, allocates the cmap, registers the framebuffer, and links the card into `card_list`.
6. Runtime fbdev mode changes go through `sisfb_check_var()` to normalize timing/depth/virtual size, then `sisfb_set_par()`/`sisfb_do_set_var()` to call `SiSSetMode()`, recalculate pitch, set CRT1/CRT2 base registers, update current mode state, and initialize acceleration when enabled.
7. Private ioctls expose heap allocation/free, vblank status, device info, auto-max y-panning, TV offsets, CRT1 switching, and a software lock bit. Raw VRAM allocation/free requires `CAP_SYS_RAWIO`.
8. Removal unmaps MMIO/VRAM, releases regions, frees copied ROM and PCI references, removes the WC mapping, disables a device the driver had enabled, unregisters the framebuffer, and notes that restoring the original text mode is not supported.

## State And Persistence Behavior
- Global boot/module parameter variables in `sis_main.h` and this file are process-wide until copied into each probed `sis_video_info`.
- Per-card state lives in `struct sis_video_info`: display mode, current virtual base, monitor ranges, bridge flags, VRAM layout, heap lists, BIOS copy pointer, register-derived detection results, acceleration state, card linkage, and private ioctl data.
- Hardware state is persistent and side-effectful: VGA sequencer/CRTC registers, bridge `PART1..PART5` registers, Chrontel encoder registers, PCI config dwords/bytes, command queue MMIO registers, VRAM test patterns during POST, and write-combining mappings are all changed.
- `modechanged`, `modeprechange`, `currentvbflags`, `sisfb_lastrates[]`, TV offset backups, and detected PDC/EMI values preserve runtime choices across later mode changes and private ioctls.
- The VRAM heap persists for the lifetime of the card. Allocations are offset/size nodes in used/free lists; freed blocks are coalesced with adjacent free nodes. `sisfb_heap` is a global pointer to the first card's heap for legacy external callers, so multi-card behavior is intentionally limited.

## Dependencies And Integration Points
- Kernel subsystems: PCI core, fbdev core, aperture conflict removal, memory resource reservation, IO mappings, write-combining APIs, user-copy helpers, capabilities, module parameters, and kernel logging.
- Local driver headers and code: `sis.h`, `sis_main.h`, `init301.h`, `vgatypes.h`, `vstruct.h`, `sis_accel.c`, `init.c`, and `init301.c`.
- External ABI: standard fbdev operations and SiS-specific ioctls from `<video/sisfb.h>` such as `SISFB_GET_INFO`, `SISFB_COMMAND`, `SISFB_SET_TVPOSOFFSET`, `FBIO_ALLOC`, and `FBIO_FREE`.
- Hardware interfaces: VGA IO ports initialized by `SiSRegInit()`, PCI BAR0 framebuffer, BAR1 MMIO, BAR2 relocated IO, optional PCI ROM, northbridge/LPC devices, video bridges, DDC/EDID, and Chrontel/SiS bridge I2C-like accesses.

## Risks And Edge Cases
- This driver directly writes hardware registers and can POST cards. Incorrect chip/bridge detection, ROM parsing, or parameter choices can leave the display blank or hardware in a changed state after unload.
- `sisfb_remove()` unmaps resources before unregistering the framebuffer, so any live fbdev callbacks during teardown would be hazardous if core synchronization assumptions fail.
- `sis_malloc()` and `sis_free()` dereference the global `sisfb_heap` without a NULL guard; the intended callers must only use them after first-card heap initialization and before removal invalidates it.
- The heap routines do not use an obvious lock; concurrent private ioctls or legacy DRM users could race heap metadata unless external serialization exists elsewhere.
- `sisfb_interpret_edid()` has a likely indexing bug in the fallback standard timing loop: it matches against `sisfb_ddcfmodes[j]` but then reads `sisfb_ddcsmodes[j]` fields for v/dclock, mixing arrays of different meanings.
- `sisfb_check_var()` truncates excessive offsets using `var->xres_virtual - var->xres - 1`; when virtual equals visible, underflow can produce a large unsigned-style value in signed fields depending on type conversions.
- POST routines perform VRAM write/read tests and partial ROM-indexed table reads with many chip/revision assumptions. Missing or malformed XGI ROM content could lead to bad register programming in branches that assume `bios` is valid.
- Monitor DDC validation only warns when refresh exceeds EDID ranges; it does not reject the mode.
- Text mode restoration is explicitly not implemented on unload after mode changes.

## Test Signals
- Build coverage under `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, built-in, and module configurations is critical because large blocks are compile-time conditional.
- Static checks should focus on user-copy/ioctl paths, global heap lifetime, teardown ordering, unchecked ROM offsets, and arithmetic in `sisfb_check_var()`/heap sizing.
- Runtime smoke tests require target hardware or emulation with matching PCI IDs: probe success, `register_framebuffer`, mode setting via `fbset`, panning, blank/unblank, colormap writes, private ioctls, module unload, and no resource leaks.
- Hardware-specific validation should exercise unposted-card paths, ROM-disabled paths, CRT1-only, LCD, TV, secondary VGA, SiS bridge, Chrontel bridge, DDC failure/corrupt EDID, y-panning max, noaccel, forced CRT2, TV offset, PDC, and XGI Z7/Z9 detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.h

## Purpose
`sis_main.h` is not a conventional declaration-only header. It is included by `sis_main.c` and provides static driver data: the default fbdev `var`, boot/module parameter globals, supported PCI ID table, supported chip metadata, mode tables, refresh-rate tables, LCD-panel mappings, CRT2/TV option mappings, EDID fallback timing tables, and board-specific special timing quirks.

## Important APIs, Types, And Tables
- `my_default_var` initializes a neutral `fb_var_screeninfo` that `sisfb_probe()` copies before filling mode-specific fields.
- Boot parameter globals such as `sisfb_off`, `sisfb_parm_mem`, `sisfb_accel`, `sisfb_ypan`, `sisfb_mode_idx`, `sisfb_crt1off`, `sisfb_crt2type`, `sisfb_pdc`, `sisfb_scalelcd`, `sisfb_specialtiming`, `sisfb_tvplug`, `sisfb_tvstd`, and TV offset variables are parsed by `sis_main.c`.
- `sisfb_chip_info[]` maps each supported PCI table entry to the logical chip, VGA engine generation, mode-number index, hardware cursor reservation size, bridge write-enable register, and display name.
- `sisfb_pci_table[]` is the module PCI match table, gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`, and exported via `MODULE_DEVICE_TABLE`.
- `sisbios_mode[]` maps user-facing mode names and VESA IDs to SiS BIOS mode numbers for both 300 and 315 engines, resolution/depth, default refresh index, text geometry, and supported chipset generation.
- `sis_lcd_data[]`, `sis300paneltype[]`, `sis310paneltype[]`, and `sis661paneltype[]` convert hardware panel IDs to LCD resolution and default mode index.
- `sis_crt2type[]` and `sis_tvtype[]` parse boot/module strings for forced CRT2 output and TV standard selection.
- `sisfb_vrate[]` defines supported refresh indexes per resolution plus a SiS730 32bpp validity flag.
- `sisfb_ddcsmodes[]` and `sisfb_ddcfmodes[]` provide EDID fallback range inference for established and standard timings.
- `mychswtable[]` and `mycustomttable[]` encode vendor/subsystem/BIOS-specific quirks for Chrontel setup and special timings. Special timing constants come from `vstruct.h`.

## Control Flow And Use
- `sisfb_setdefaultparms()` initializes the globals declared here.
- Built-in and module parameter parsing updates these globals before PCI probing starts.
- `sisfb_probe()` copies the global configuration into each card's `sis_video_info` and uses the static tables to choose chip behavior, default modes, LCD resolution, bridge output, refresh rate, and special timing.
- Mode search functions scan `sisbios_mode[]`; validation later checks bridge-specific low-level support before using a mode.
- Custom timing detection compares the running card's chip ID, BIOS version/date/checksum/footprints, and PCI subsystem IDs against `mycustomttable[]`.

## State And Persistence Behavior
- All variables are `static` in this header, so they have internal linkage in the including translation unit and persist for the lifetime of the module/built-in driver.
- The table data is read-only by design except for globals changed by option parsing. `sisfb_mode_idx` and related option globals become the seed values for all later cards.
- Because this is a header with definitions, it should not be included by multiple C files without creating separate private copies of the static data.

## Dependencies And Integration Points
- Depends on `vstruct.h` for `CUT_*` custom timing constants and on `sis.h` for chip IDs, bridge flags, PCI vendor/device IDs, cursor constants, and LCD/TV flag values.
- The PCI table integrates with the kernel PCI core through `sisfb_driver`.
- The mode, refresh, and panel tables integrate with low-level mode-setting functions in `init.c`/`init301.c`, which consume SiS BIOS mode numbers, refresh indexes, panel types, and bridge flags.

## Risks And Edge Cases
- The header defines substantial storage, so accidental inclusion outside `sis_main.c` would duplicate independent state and tables.
- `sisbios_mode[]` comments indicate some 24bpp user strings map to 32bpp framebuffer depth; callers must treat `bpp` as actual driver depth, not literal user text.
- Forced CRT2/TV parameters are parsed before hardware is known; `sisfb_detect_VB_connect()` must later reject incompatible requests.
- Special timing detection relies on hard-coded BIOS offsets/checksums and subsystem IDs, so unsupported revisions may silently miss required quirks.
- Table index constants such as `DEFAULT_MODE`, `MODE_FSTN_8`, and LCD default indexes must stay aligned with `sisbios_mode[]` order.

## Test Signals
- Compile with both SiS config variants to ensure PCI table and chip tables align with `ent->driver_data`.
- Test mode parsing for names, fuzzy `XxY-Depth@Rate` strings, VESA numbers, FSTN/DSTN paths, and invalid values.
- Validate that every default mode index, LCD default index, and chipset flag points to an entry accepted by `sisfb_validate_mode()` on the intended engine.
- Exercise custom timing command-line options and autodetection with representative subsystem IDs/ROM data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vgatypes.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vgatypes.h

## Purpose
`vgatypes.h` supplies base type definitions for the SiS universal mode-setting code. In this kernel copy it mainly defines the IO address type, the `__iomem` annotation macro used by shared structures, and the canonical `SIS_CHIP_TYPE` enumeration.

## Important APIs And Types
- `SISIOMEMTYPE` is first defined empty, then `linux/types.h` is included, and `SISIOMEMTYPE` is redefined to `__iomem`. `vstruct.h` uses it to annotate memory-mapped pointers inside `struct SiS_Private`.
- `typedef unsigned long SISIOADDRESS;` represents VGA/bridge IO port base addresses and relocated IO addresses used by `SiS_SetReg*()`/`SiS_GetReg*()`.
- `SIS_CHIP_TYPE` enumerates logical chip families: legacy/old chips, SiS 300/540/630/730, SiS 315/550/650/740/330/661/741/670/660/760/761/762/770/340/341/342, XGI 20/21/40, and `MAX_SIS_CHIP`.

## Control Flow And Use
- There is no runtime control flow; this file is consumed at compile time by `sis.h` and `vstruct.h`.
- `sis_main.c` stores chip IDs in `ivideo->chip`, `ivideo->chip_real_id`, and `SiS_Pr.ChipType` using these values and switches on them for DRAM sizing, bridge detection, POST, and mode validation.
- `SISIOADDRESS` flows through register access function prototypes and `struct SiS_Private` fields for sequencer, CRTC, DAC, bridge, capture, and playback ports.

## State And Persistence Behavior
- The enum values are ABI-like internal constants. Several values are explicitly numbered, such as `SIS_660 = 35`, `SIS_340 = 55`, and `XGI_20 = 75`, preserving compatibility with shared SiS mode-setting code.
- No mutable state is defined here.

## Dependencies And Integration Points
- Includes `<linux/types.h>` solely to get `__iomem`.
- Integrated by `sis.h`, `vstruct.h`, and any low-level mode-setting source that needs chip IDs or IO address typing.
- Bridges hardware-specific branches in `sis_main.c` and low-level init code by giving both layers a shared chip taxonomy.

## Risks And Edge Cases
- Changing enum numeric values would break switch logic and shared tables that rely on stable chip family ordering or explicit IDs.
- `SISIOADDRESS` as `unsigned long` is suitable for port-like addresses in this driver but should not be treated as a pointer; memory-mapped pointers use `SISIOMEMTYPE`.
- `SISIOMEMTYPE`'s redefine pattern is unusual; include-order changes could accidentally lose or duplicate sparse annotations.

## Test Signals
- Sparse/build checks should confirm `__iomem` annotations remain valid after including this header.
- Compile all files using `SIS_CHIP_TYPE` switches to catch missing cases after enum edits.
- Runtime chip detection for SiS and XGI cards should map PCI IDs to the expected enum values in `sisfb_chip_info[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vgatypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vstruct.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vstruct.h -->
