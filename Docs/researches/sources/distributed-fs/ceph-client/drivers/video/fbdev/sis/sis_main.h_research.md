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
