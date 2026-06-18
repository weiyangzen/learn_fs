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
