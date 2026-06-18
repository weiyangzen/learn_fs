# subset-b-005570 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-main.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-main.c

Purpose: this is the central OMAP2/3 fbdev implementation. It binds the platform device named `omapfb`, discovers OMAP DSS displays, overlays, and overlay managers, allocates `fb_info` instances, allocates DMA framebuffer memory, programs DSS overlays from `fb_var_screeninfo`, and exposes fbdev operations for mode changes, panning, mmap, blanking, color maps, and OMAP-specific ioctls implemented elsewhere.

Important APIs/types/functions: module parameters `mode`, `vram`, `rotate`, `vrfb`, `mirror`, `auto_update`, and `auto_update_freq` shape initial state. `omapfb_colormodes[]`, `fb_mode_to_dss_mode()`, and `dss_mode_to_fb_mode()` translate between fbdev formats and DSS color modes, including nonstandard YUV identifiers. `check_fb_var()`, `check_fb_size()`, `check_vrfb_fb_size()`, `set_fb_fix()`, and `setup_vrfb_rotation()` validate and normalize framebuffer geometry, color format, physical layout, and VRFB mappings. `omapfb_setup_overlay()` and `omapfb_apply_changes()` are the core DSS programming path. `omapfb_mmap()` maps the physical framebuffer into userspace and tracks mappings with `omapfb2_mem_region.map_count`. Probe/remove are handled by `omapfb_probe()` and `omapfb_remove()`.

Control flow: probe defers until DSS is initialized, creates `omapfb2_device`, validates VRFB support, initializes DSS compatibility, records display devices, overlays, and managers, finds a default display, connects displays, binds overlays to the default manager, applies module/default/EDID modes, creates framebuffers, applies manager state, initializes the default display, then creates sysfs files. `omapfb_create_framebuffers()` allocates `fb_info` objects, assigns one overlay per framebuffer initially, allocates VRAM for fb0 or configured framebuffers, initializes each `fb_info`, registers each framebuffer, applies overlay state, and enables fb0. Runtime `fb_check_var` takes a read lock on the memory region, `fb_set_par` refreshes fix fields and VRFB before programming overlays, and `fb_pan_display` changes offsets then re-applies overlays.

State and persistence behavior: all state is in kernel memory and hardware registers. `omapfb2_device` owns framebuffers, display metadata, manager/overlay pointers, a pseudo palette, and an optional auto-update workqueue. `omapfb_info` stores overlay assignment, per-overlay rotation, rotation type, mirror flag, and the memory region. `omapfb2_mem_region` stores DMA allocation token/handle, physical/virtual addresses, VRFB context, size, map count, and locking. No on-disk persistence exists; module parameters and display EDID/defaults seed state at load time. Manual-update displays may keep a delayed work item active until blank/remove stops it.

Dependencies and integration points: integrates with fbdev core (`struct fb_ops`, `register_framebuffer`, cmap, fb modedb, EDID helpers), DMA API (`dma_alloc_attrs`, write-combine/no-kernel-mapping attributes), VM mmap helpers, OMAP DSS (`omap_dss_device`, overlays, managers, timings, manual update), OMAP VRFB exported APIs, platform driver registration, and sysfs/ioctl siblings via prototypes in `omapfb.h`.

Risks: mode validation mutates requested `var` values, which is expected for fbdev but can surprise callers. VRFB reconfiguration while mapped is called out as unsafe in comments; sysfs size changes block active mmap but `setup_vrfb_rotation()` itself notes it should not be allowed while mmapped. Overlay/sysfs changes depend on correct locking order between fbdev locks, `fbdev->mtx`, and memory-region rwsems. `omapfb_parse_vram_param()` accepts but warns that fixed physical addresses are unsupported. Hardware programming error paths can leave partially connected displays/overlays until cleanup. Auto-update frequency falls back to 20 Hz, but a too-high module value could create frequent workqueue activity.

Test signals: useful checks are probe on hardware or emulated board with DSS initialized, fbdev mode setting through `fbset`, mmap/open/close map-count behavior, sysfs-driven size/overlay/rotation changes, panning with all rotations, YUV and RGB format conversion, manual-update display blank/unblank with TE enabled, VRFB enabled/disabled boots, failure injection for DMA allocation and VRFB context exhaustion, and remove/unbind cleanup with active framebuffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-sysfs.c

Purpose: this file adds per-framebuffer sysfs controls for OMAP fbdev instances. It lets users inspect and mutate rotation type, mirroring, attached overlays, per-overlay rotation, allocated framebuffer size, physical/virtual addresses, and display update mode.

Important APIs/types/functions: `omapfb_attrs[]` defines attributes `rotate_type`, `mirror`, `size`, `overlays`, `overlays_rotate`, `phys_addr`, `virt_addr`, and `update_mode`. `show_*` functions format state from `fb_info`/`omapfb_info`; `store_*` functions parse user input with `kstrtoint`, `kstrtobool`, `kstrtoul`, or legacy `simple_strtoul`. `store_overlays()` uses `get_overlay_fb()` to prevent assigning an overlay to more than one framebuffer. `store_size()` calls `omapfb_realloc_fbmem()` after ensuring the region is not mapped and no users of that region have enabled overlays. `omapfb_create_sysfs()` and `omapfb_remove_sysfs()` attach/remove attributes to each fb device.

Control flow: each store path obtains `lock_fb_info()` before modifying framebuffer-visible state. Overlay assignment additionally takes `omapfb_lock(fbdev)` to protect cross-framebuffer overlay ownership. Rotation type can only change when the memory region has no allocated size. Mirror and overlay rotation validate a copied `fb_var_screeninfo`, update fix fields or overlay setup, and call `omapfb_apply_changes()`. Overlay list changes detach removed overlays by disabling them and applying the manager, compacts arrays, appends new overlays, then re-applies the framebuffer if anything was added. Size changes take the memory-region write semaphore directly, increment lock count, block active mmaps and enabled overlays, then reallocate.

State and persistence behavior: sysfs writes mutate in-memory driver state and hardware overlay/display programming; there is no persistence across module unload/reboot. The visible physical/virtual address attributes expose the current memory region fields. Size changes may free and recreate DMA memory and clear or reinitialize `fb_info` state. Update-mode changes delegate to ioctl/update-mode helpers declared in `omapfb.h`, affecting manual-update work scheduling in the main file.

Dependencies and integration points: depends on fbdev device association through `dev_get_drvdata()`, OMAP DSS overlay objects, OMAPFB locking helpers and memory-region model, `omapfb_apply_changes()`, `check_fb_var()`, `set_fb_fix()`, `omapfb_realloc_fbmem()`, and OMAP update-mode helpers. It is created and removed by the main platform driver after framebuffers are registered.

Risks: input parsing manually increments through comma-separated overlay lists and rotations, so malformed delimiters can produce fragile behavior. `if (ovlnum > fbdev->num_overlays)` should conceptually be `>=` to avoid indexing one past the last overlay. Error handling in overlay detach can leave earlier detach operations applied if a later step fails. `virt_addr` exposes a kernel pointer through sysfs, which is normal for old drivers but undesirable under modern hardening expectations. Size reallocation is intentionally blocked while mapped/enabled, but other state changes rely on caller locking and can still race with display activity if lower DSS callbacks behave unexpectedly.

Test signals: write/read each sysfs attribute, invalid rotation and overlay lists, overlay stealing attempts between framebuffers, size changes with active mmap returning `-EBUSY`, size zero and resize-back flows, mirror toggles while displaying, update-mode transitions on manual-update panels, and sysfs cleanup during driver remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb.h

Purpose: this internal header defines the shared OMAP fbdev data model, debug macro, locking helpers, and cross-file function prototypes used by the main, sysfs, ioctl, and VRFB-related code.

Important APIs/types/functions: `FB2OFB()` converts `fb_info->par` to `struct omapfb_info`. `struct omapfb2_mem_region` holds DMA/VRFB memory state, address fields, allocation flags, map count, and rwsem/lock count. `struct omapfb_info` is appended to each `fb_info` and records framebuffer id, memory region, overlay list, owning `omapfb2_device`, rotation type, per-overlay rotations, and mirror state. `struct omapfb_display_data` tracks a DSS display, bpp override, update mode, and delayed auto-update work. `struct omapfb2_device` is the driver root object containing displays, overlays, managers, framebuffer array, regions, pseudo palette, mutex, and workqueue. Inline helpers include `fb2display()`, `get_display_data()`, `omapfb_lock()`, `omapfb_unlock()`, `omapfb_overlay_enable()`, `omapfb_get_mem_region()`, and `omapfb_put_mem_region()`.

Control flow: the header does not execute standalone, but it defines the locking and ownership conventions. Callers use `omapfb_get_mem_region()`/`omapfb_put_mem_region()` around region-sensitive operations, causing read locking and `lock_count` accounting. `fb2display()` resolves the display through the first attached overlay. `get_display_data()` linearly searches the driver display array and `BUG()`s if the display is unknown.

State and persistence behavior: all structures are volatile kernel runtime state. The fixed-size arrays support up to 10 framebuffers/regions/displays/overlays/managers and up to 3 overlays per framebuffer. No persistent storage is defined; module parameters and detected DSS topology populate these structures at probe time.

Dependencies and integration points: includes Linux rwsem and DMA mapping APIs plus OMAP DSS headers. Prototypes link to `omapfb-main.c`, `omapfb-sysfs.c`, ioctl/update-mode implementation files, and auto-update helpers. The memory region embeds `struct vrfb` from `<video/omapvrfb.h>` through transitive includes in source users.

Risks: array sizes are fixed and rely on probe code not exceeding them when enumerating DSS devices/overlays/managers. `get_display_data()` fails with `BUG()` rather than a recoverable error, so callers must only pass known DSS devices. `fb2display()` assumes the first overlay is representative, which can be limiting when a framebuffer drives multiple overlays. Lock-count is diagnostic/guard state and must stay paired with rwsem operations.

Test signals: build coverage across all OMAPFB compilation units, lockdep during sysfs and fbdev mode changes, enumeration with multiple displays/overlays, no-overlay framebuffers returning `NULL` display, and stress around memory-region map/reallocation lock pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/omapfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/vrfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/vrfb.c

Purpose: this built-in platform driver manages the OMAP VRFB rotation engine. It allocates VRFB contexts, reserves the four rotated virtual memory windows per context, programs SMS rotation registers, maps rotation views, computes sizing constraints, and restores hardware context after power-management events.

Important APIs/types/functions: exported symbols are `omap_vrfb_restore_context()`, `omap_vrfb_adjust_size()`, `omap_vrfb_min_phys_size()`, `omap_vrfb_max_height()`, `omap_vrfb_setup()`, `omap_vrfb_map_angle()`, `omap_vrfb_release_ctx()`, `omap_vrfb_request_ctx()`, and `omap_vrfb_supported()`. Internal `struct vrfb_ctx` stores per-context base, physical base, control, and size registers. `ctx_map`, `ctx_lock`, `ctxs`, `num_ctxs`, `vrfb_base`, and `vrfb_loaded` are global driver state.

Control flow: `vrfb_probe()` maps the SMS register resource, counts remaining resources as VRFB contexts, allocates `ctxs`, stores context base addresses, and marks the engine loaded. Clients call `omap_vrfb_request_ctx()` to find a free context under `ctx_lock`, reserve four `OMAP_VRFB_SIZE` windows, and fill `vrfb->paddr[]`; on failure it releases partial reservations. `omap_vrfb_setup()` computes page-aligned virtual dimensions, handles YUV packed-pixel adjustment, stores/restores register values in `ctxs`, writes SMS registers, and records offsets/bytespp in the caller's `struct vrfb`. `omap_vrfb_map_angle()` ioremaps a rotated view with write-combining. `omap_vrfb_release_ctx()` releases reserved windows and clears the bitmap. Restore iterates reserved contexts and reprograms registers.

State and persistence behavior: context allocation and programmed register snapshots are global in-memory state. Physical VRFB windows are reserved through the resource tree while a context is held. Hardware register content is not persistent and is restored from `ctxs` by explicit PM restore. `vrfb_loaded` is a runtime capability flag used by OMAPFB module parameter handling.

Dependencies and integration points: depends on platform resources named by the OMAP platform, IO memory accessors, resource reservation, mutex/bit operations, and `<video/omapvrfb.h>` definitions such as `struct vrfb` and `OMAP_VRFB_LINE_LEN`. OMAPFB uses it for VRFB-assisted rotation and size validation.

Risks: `ctx_map` is an `unsigned long`, so systems exposing more contexts than bits would be unsafe, though hardware context counts are small. `omap_vrfb_setup()` uses `BUG()` for unsupported bytes-per-pixel values. Release assumes the context is reserved and uses `BUG_ON()` if accounting is inconsistent. Mapping sizes depend on height and `OMAP_VRFB_LINE_LEN`; incorrect caller geometry can create unusable mappings. PM restore is lockless by design and relies on no concurrent clients during wake.

Test signals: platform probe with multiple context resources, request/release exhaustion and partial reservation failure, min-size/max-height computations for RGB and YUV, mapping all rotation angles, OMAPFB boot with `vrfb=y`, suspend/resume context restoration, and resource leak checks after repeated framebuffer allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/vrfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/p9100.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/p9100.c

Purpose: this is a SPARC/SBus-style platform framebuffer driver for Weitek/Power 9100 devices. It registers an 8-bpp pseudocolor fbdev, maps P9100 control registers and framebuffer memory, supports RAMDAC palette writes, display blanking, mmap through SBus helpers, and cg3-compatible ioctl behavior.

Important APIs/types/functions: `struct p9100_regs` describes system, video, VRAM, and IBM RGB528 RAMDAC registers. `struct p9100_par` stores a spinlock, mapped registers, blank flag, and SBus IO selector. `p9100_setcolreg()` writes 8-bit palette values to RAMDAC registers under spinlock. `p9100_blank()` toggles `SCREENPAINT_TIMECTL1_ENABLE_VIDEO`. `p9100_sbusfb_mmap()` and `p9100_sbusfb_ioctl()` delegate to `sbusfb_mmap_helper()` and `sbusfb_ioctl_helper()`. `p9100_probe()` and `p9100_remove()` own platform lifecycle.

Control flow: init exits if `fb_get_options("p9100fb")` disables the driver, then registers the platform driver. Probe allocates `fb_info`, initializes the lock, derives framebuffer physical resource and SBus IO bits, fills fixed and variable screen info from Open Firmware, maps control registers and VRAM, unblanks video, allocates a 256-entry cmap, initializes `fix`, registers fbdev, loads the cmap, and stores driver data. Remove unregisters fbdev, frees cmap, unmaps registers/framebuffer, and releases `fb_info`.

State and persistence behavior: state lives in mapped P9100 registers, RAMDAC palette contents, and `fb_info`. The blank flag is maintained in `par->flags` but hardware enable is the effective state. No persistent storage is used; geometry comes from OF properties such as `linebytes`.

Dependencies and integration points: uses Linux fbdev, Open Firmware device nodes/resources, SPARC asm fbio definitions, SBus framebuffer helper macros (`FB_DEFAULT_SBUS_OPS`, mmap/ioctl helpers), and platform driver matching by OF name `p9100`.

Risks: the driver assumes platform resources by index, with resource 2 as framebuffer and resource 0 as registers. Palette writes are serialized, but mmap and blanking depend on correct SBus helper behavior. Ioctl intentionally presents as `FBTYPE_SUN3COLOR`, which may hide P9100-specific capability from userland. No explicit `request_mem_region()` is used around OF mappings in this file.

Test signals: OF/platform bind on a `p9100` node, register and framebuffer map failures, fbcon palette changes, `FBIOGTYPE`/SBus ioctl compatibility, mmap of `CG3_MMAP_OFFSET`, blank/unblank transitions, and remove after registered framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/p9100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.c

Purpose: this PowerMac platform framebuffer driver supports Apple "platinum" onboard video. It maps Platinum registers, framebuffer memory, and DACula colormap registers, detects installed VRAM and DAC type, selects a Mac video/color mode from boot options, NVRAM, monitor sense, and VRAM limits, programs timing/clock/register tables from `platinumfb.h`, and registers a fbdev.

Important APIs/types/functions: `struct fb_info_platinum` stores selected vmode/cmode, cached geometry, software palette, pseudo palette, mapped cmap and Platinum registers, framebuffer base/physical address, VRAM size, clock/DAC type, and resources. fbdev callbacks are `platinumfb_check_var()`, `platinumfb_set_par()`, `platinumfb_setcolreg()`, and `platinumfb_blank()`. Internal helpers include `platinum_vram_reqd()`, `read_platinum_sense()`, `set_platinum_clock()`, `platinum_set_hardware()`, `platinum_init_info()`, `platinum_init_fb()`, `platinum_var_to_par()`, and `platinumfb_setup()`.

Control flow: init parses `video=platinumfb:` options for built-in use and registers an OF platform driver matching `platinum`. Probe allocates `fb_info`, reads register/framebuffer resources, requests the framebuffer region, maps up to 4 MiB framebuffer, maps registers and hard-coded cmap registers, probes VRAM banks by writing sentinel bytes, detects DACula type to choose clock table, stores driver data, and calls `platinum_init_fb()`. Initialization reads monitor sense and optionally NVRAM, picks a safe vmode/cmode, falls back to 640x480x8 if needed, initializes fixed info/cmap, calls `fb_set_var()` to trigger hardware programming, and registers the framebuffer. `set_par` converts var to driver mode, programs hardware, and updates `screen_base`, `smem_start`, visual, and line length.

State and persistence behavior: selected defaults may come from NVRAM, but the driver itself only mutates runtime hardware and `fb_info` state. Palette writes are cached in `pinfo->palette` and sent to DACula. The mode tables in the header are static data. Remove unregisters and unmaps resources; it does not restore original firmware mode.

Dependencies and integration points: depends on PowerMac/macmodes helpers (`mac_vmode_to_var`, `mac_var_to_vmode`, monitor-sense mapping), NVRAM when reachable, OF platform resources, big-endian register accessors, fbdev cmap/mode callbacks, and `platinumfb.h` register tables.

Risks: cmap register physical address is hard-coded to `0xf301b000` rather than coming from firmware. Error paths after cmap `request_mem_region()` are incomplete in probe failure after `platinum_init_fb()` and may leak requested regions. `platinumfb_set_par()` prints line length unconditionally with `printk()`. Blank is effectively a stub. VRAM probing writes into framebuffer memory and relies on cache invalidation. The line-length formula includes offsets and mode quirks that need hardware validation.

Test signals: boot on compatible PowerMac with different VRAM sizes and DACula types, boot options `vmode:`/`cmode:`, NVRAM default modes, monitor-sense fallback, modes rejected for insufficient VRAM, palette changes in 8/16/32 bpp, framebuffer registration and remove/unmap, and visual/line_length correctness after `fbset`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.h

Purpose: this header provides the hardware register layout and static mode programming tables consumed by `platinumfb.c`. It is effectively the data sheet encoding for Apple Platinum timing, pitch, DACula, and clock setup.

Important APIs/types/functions: `struct cmap_regs` maps DACula indexed address/data/LUT registers with 16-byte spacing. `struct preg` and `struct platinum_regs` model padded 32-bit Platinum registers. `struct platinum_regvals` packages framebuffer offset, pitch per color mode, 26 timing/control register values, per-cmode offsets, modes, DACula controls, and two clock-parameter variants. `platinum_reg_init_1` through `_20` define Mac video mode tables. `platinum_reg_init[VMODE_MAX]` indexes those tables by Mac vmode. `struct vmode_attr` and `vmode_attrs[]` expose resolution, refresh, and interlace metadata.

Control flow: no executable control flow exists here, but `platinumfb.c` indexes `platinum_reg_init[pinfo->vmode - 1]` during hardware programming, mode validation, framebuffer offset computation, clock setup, and line-length calculation. The `clock_params[2][2]` entries are selected by detected DACula/clock type.

State and persistence behavior: all state is static kernel data. It is read-only in normal operation, though the definitions are not declared `const`. It encodes persistent hardware knowledge rather than runtime state.

Dependencies and integration points: depends on `VMODE_MAX` and color-mode indices from `macmodes.h`. Its tables must align with `mac_vmode_to_var()` and `mac_var_to_vmode()` expectations. The register offsets and pitches are interpreted by `platinum_set_hardware()` and `set_platinum_clock()`.

Risks: tables are hand-coded magic values; a wrong value can damage display timing or produce unusable video. `platinum_reg_init` assumes every vmode from 1 to `VMODE_MAX` has a corresponding table and matching `vmode_attrs` entry. Because tables are mutable static objects, accidental writes would affect all devices. Some comments mark duplicated/unsupported modes, e.g. 800x600 56 Hz copied from another mode.

Test signals: compile with PowerMac/macmodes constants, mode-by-mode validation via `fbset`, visual confirmation for each supported resolution/refresh/color depth, DACula old/new clock parameter selection, VRAM-limited modes using pitch/offset tables, and regression tests comparing `vmode_attrs` to `macmodes` conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pm2fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/pm2fb.c

Purpose: this PCI fbdev driver supports 3Dlabs Permedia2, Permedia2V, and TI TVP4020 devices. It handles PCI resource setup, framebuffer and MMIO mapping, mode validation/programming, RAMDAC and clock setup, hardware acceleration for rectangle/copy/1-bpp image operations, hardware cursor, panning, blanking, and write-combining/MTRR setup.

Important APIs/types/functions: `struct pm2fb_par` stores board type, mapped registers, memory clock and saved memory controller values, cached video flags, pseudo palette, and write-combining cookie. Low-level accessors include `pm2_RD()`, `pm2_WR()`, RDAC helpers, and `WAIT_FIFO()`. Clock helpers `pm2_mnp()` and `pm2v_mnp()` calculate PLL parameters. Hardware setup is split across `reset_card()`, `reset_config()`, `set_aperture()`, `set_memclock()`, `set_pixclock()`, and `set_video()`. fbdev callbacks include `pm2fb_check_var()`, `pm2fb_set_par()`, `pm2fb_setcolreg()`, `pm2fb_pan_display()`, `pm2fb_blank()`, `pm2fb_sync()`, accelerated drawing callbacks, and cursor callbacks for Permedia2 and Permedia2V.

Control flow: module/built-in init checks `fb_modesetting_disabled()`, parses options when built in, and registers a PCI driver. Probe removes conflicting aperture users, enables PCI, allocates `fb_info`, classifies device id, maps MMIO with endian-specific offset, saves/restores memory config, infers framebuffer size from memory-bank config, maps linear framebuffer write-combined, optionally adds write-combining, initializes fbops/fix/pixmap/flags, disables acceleration if requested, chooses a mode with `fb_find_mode()` or fallback, allocates cmap, and registers fbdev. `pm2fb_set_par()` resets the card, restores memory config, clears palette, sets clocks, computes timing registers in 32/64-bit units, programs framebuffer and RAMDAC format registers, and enables video according to activation.

State and persistence behavior: runtime state is device-local in `pm2fb_par`, hardware registers, RAMDAC palette/cursor RAM, and fbdev structures. Module parameters `mode_option`, `lowhsync`, `lowvsync`, `noaccel`, `hwcursor`, and `nomtrr` persist only while the module is loaded. The original memory configuration captured at probe is reused after resets. Remove unregisters fbdev, removes write-combining, unmaps resources, frees pixmap/cmap, and disables PCI.

Dependencies and integration points: depends on PCI core, aperture conflict removal, fbdev core and cfb fallbacks, architecture write-combining helpers, `<video/permedia2.h>` register definitions, optional CVisionPPC memory timing constants, endian configuration, and module parameter/fb boot option parsing.

Risks: FIFO wait loops can spin forever if hardware is wedged. Only one-board support is noted as historically weak because globals like `pm2fb_fix` and module options are shared. Hardware acceleration clips inputs but still depends on correct pixmap alignment and FIFO accounting. PLL search loops use wrapping unsigned loop variables and old hardware assumptions. Probe error paths are extensive and need resource-pair correctness. Big-endian aperture handling and 24-bpp color order are subtle. `nomtrr` parameter description is confusing relative to bool behavior.

Test signals: PCI IDs for all supported devices, resource conflict with EFI/VGA aperture, endian builds, mode validation for 8/16/24/32 bpp and invalid virtual x/interlace/pixclock, blank modes, panning yoffset, accelerated fill/copy/image with fallback disabled/enabled, hardware cursor shape/color/position for both RAMDAC types, noaccel and nomtrr options, remove after failed probe stages, and framebuffer mmap correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pm2fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pm3fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/pm3fb.c

Purpose: this PCI fbdev driver supports 3Dlabs Permedia3 devices. It maps MMIO and framebuffer apertures, sizes board memory, validates and programs display modes, initializes the 2D engine, provides accelerated fill/copy/1-bpp image operations, hardware cursor, panning, blanking, palette/pseudo-palette handling, and optional write-combining.

Important APIs/types/functions: `struct pm3_par` stores mapped registers, cached video flags, current screen base, pseudo palette, and write-combining cookie. Register helpers are `PM3_READ_REG()`, `PM3_WRITE_REG()`, `PM3_WAIT()`, and `PM3_WRITE_DAC_REG()`. `pm3fb_calculate_clock()` picks PLL parameters. `pm3fb_depth()` and `pm3fb_shift_bpp()` normalize pixel formats and register units. Core callbacks are `pm3fb_check_var()`, `pm3fb_set_par()`, `pm3fb_setcolreg()`, `pm3fb_pan_display()`, `pm3fb_blank()`, `pm3fb_sync()`, `pm3fb_cursor()`, and acceleration callbacks. `pm3fb_size_memory()` probes framebuffer RAM.

Control flow: init checks modesetting disable state, parses built-in options, and registers the PCI driver. Probe removes aperture conflicts, enables PCI, allocates `fb_info`, maps endian-adjusted MMIO, sizes memory by temporarily mapping a 64 MiB aperture and testing 1 MiB offsets for wraparound, maps real framebuffer write-combined, records initial video control, sets fbops/fix/pseudo palette/accel flags/pixmap, selects a mode, allocates cmap, validates var, registers fbdev, and stores PCI drvdata. `pm3fb_set_par()` computes base/video flags, updates visual and line length, clears colormap, disables cursor, initializes the 2D engine, and writes display mode/timing/DAC registers.

State and persistence behavior: state is in `pm3_par`, hardware registers, framebuffer memory, cursor pattern RAM, palette, and fbdev structures. Module parameters `mode_option`, `noaccel`, `hwcursor`, and `nomtrr` affect runtime initialization only. Remove unregisters, frees cmap/pixmap, removes write-combining, unmaps resources, and releases framebuffer info.

Dependencies and integration points: depends on PCI, aperture helpers, fbdev/cfb fallback paths, architecture write-combining, `<video/pm3fb.h>` register definitions, and module/fb boot option parsing. It shares design patterns with `pm2fb.c` but has its own Permedia3 register model.

Risks: memory sizing writes test patterns into the framebuffer aperture and assumes safe access before full card-specific setup. FIFO wait loops can hang on broken hardware. `pm3fb_probe()` returns `-ENOMEM` on framebuffer allocation without disabling an already enabled PCI device, which is a cleanup asymmetry. Only 8/16/32 bpp are accepted; 24 bpp is absent unlike pm2. Register programming has special sync behavior comments for Oxygen VX1, so changes around blank/mode sync are risky. Globals like `pm3fb_fix` are shared across possible devices.

Test signals: PCI bind/unbind on supported id, failed memory-size probe, mode validation boundaries up to 2048x4095 and memory limits, 8/16/32 bpp visuals, panning and screen base updates, all blank modes, accelerated drawing and cfb fallback with `noaccel`, hardware cursor update paths, write-combining enabled/disabled, big-endian aperture mode writes, and cleanup after each probe failure label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pm3fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-aa-fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-aa-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAG-AA monochrome framebuffer cards. It maps the Bt455 RAMDAC, Bt431 cursor generator, and framebuffer memory, initializes a 1-bit effective monochrome display exposed as 8 bpp, implements blanking through the colormap, and supports hardware cursor operations.

Important APIs/types/functions: `struct aafb_par` stores the MMIO base and typed Bt455/Bt431 register pointers. `aafb_defined` and `aafb_fix` define 1280x1024 display geometry, 2048-byte virtual line stride, grayscale/pseudocolor characteristics, mono visual, and resource lengths. `aafb_cursor()` validates cursor size and delegates position, cmap, shape/image, erase, and enable operations to Bt431/Bt455 helpers. `aafb_blank()` writes black or white into colormap entry 1. Probe/remove are `pmagaafb_probe()` and `pmagaafb_remove()`.

Control flow: init registers a TC driver unless boot options disable it. Probe allocates `fb_info`, sets fbops/fix/var, reserves the whole TC slot resource, maps the MMIO window from Bt455 through before framebuffer memory, derives Bt455 and Bt431 pointers, maps framebuffer memory, initializes the two-entry monochrome colormap, erases and initializes the cursor generator, registers fbdev, takes a device reference, and logs the device. Remove drops the reference, unregisters, unmaps framebuffer/MMIO, releases the TC resource, and releases `fb_info`.

State and persistence behavior: state is hardware register contents plus `fb_info`; no disk persistence exists. The cursor image lives in Bt431 hardware. Blank state is represented by a RAMDAC colormap entry rather than a separate driver flag.

Dependencies and integration points: depends on the TurboChannel bus, fbdev default I/O-memory operations, Linux IO mapping/resource APIs, and local `bt455.h`/`bt431.h` helper APIs. Matching uses TC vendor/product strings `DEC` and `PMAG-AA`.

Risks: pointer arithmetic on `void __iomem *` is compiler-extension style but common in this tree. There is no cmap allocation because the monochrome DAC is managed directly, so fbdev colormap expectations are narrow. Cursor color maps logical fg/bg to 0x0/0xf only. The framebuffer is exposed as 8 bpp though only the least significant bit is meaningful.

Test signals: TC probe/remove, MMIO/framebuffer map failures, fbcon monochrome rendering, blank/unblank toggling colormap entry 1, cursor size rejection over `BT431_CURSOR_SIZE`, cursor position/cmap/shape updates, and resource release after failed register_framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-aa-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-ba-fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-ba-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAG-BA color framebuffer cards. It exposes a fixed 1024x864 8-bpp pseudocolor framebuffer, maps Bt459 RAMDAC registers and framebuffer memory, programs palette entries, and disables the hardware cursor at probe.

Important APIs/types/functions: `struct pmagbafb_par` holds MMIO and DAC pointers. `pmagbafb_defined` and `pmagbafb_fix` define fixed geometry, timing, 1 MiB framebuffer, 1024-byte line length, and pseudocolor visual. `dac_write()`/`dac_read()` access sparse Bt459 registers. `pmagbafb_setcolreg()` writes 8-bit RGB values into the Bt459 cmap. `pmagbafb_erase_cursor()` writes the cursor control register to disable it. Lifecycle functions are `pmagbafb_probe()` and `pmagbafb_remove()`.

Control flow: init registers the TC driver unless disabled by boot options. Probe allocates `fb_info`, allocates a 256-entry cmap, sets fbops/fix/var, reserves the full TC resource, maps MMIO, derives the Bt459 pointer, maps the framebuffer, sets `screen_size`, erases the cursor, registers fbdev, grabs a device reference, and logs. Remove reverses those operations, including cmap deallocation.

State and persistence behavior: palette state is in Bt459 RAMDAC registers and fbdev cmap memory. Cursor is simply disabled; no driver cursor state is tracked. Geometry is fixed and not recalculated at runtime. No persistent storage is used.

Dependencies and integration points: depends on TurboChannel core, fbdev default IOMEM ops, Linux resource/ioremap APIs, and `<video/pmag-ba-fb.h>` offsets/constants for Bt459 and framebuffer layout. Matching uses TC strings `DEC` and `PMAG-BA`.

Risks: fixed timing/geometry means no mode validation or runtime mode changes. Sparse register addressing divides offsets by four; wrong constants would hit wrong DAC registers. Palette writes return `1` for out-of-range, matching old fbdev convention but not a negative errno. Cursor is disabled but no fb_cursor callback is provided.

Test signals: probe on a PMAG-BA TC device, cmap allocation failure, palette programming through fbcon or `fbset`, framebuffer mmap/default ops, cursor remains hidden, resource cleanup on each failure path, and remove after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmag-ba-fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmagb-b-fb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmagb-b-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAGB-B Smart Frame Buffer cards. It maps SFB control registers, Bt459 DAC registers, and framebuffer memory; reads hardware timing registers to populate fbdev geometry; estimates oscillator frequencies; exposes an 8-bpp pseudocolor framebuffer; programs palette entries; and disables the hardware cursor.

Important APIs/types/functions: `struct pmagbbfb_par` stores MMIO, framebuffer, SFB, DAC pointers, detected oscillator frequencies, and slot. `pmagbbfb_defined`/`pmagbbfb_fix` define base fbdev state and resource sizes. `sfb_write()`/`sfb_read()`, `dac_write()`/`dac_read()`, and `gp0_write()` access device registers. `pmagbbfb_setcolreg()` writes Bt459 cmap entries. `pmagbbfb_screen_setup()` decodes horizontal/vertical timing registers into `fb_var_screeninfo` and line length. `pmagbbfb_osc_setup()` measures oscillator counts against TC bus speed and sets `pixclock`.

Control flow: init registers a TC driver unless boot options disable it. Probe allocates `fb_info`, allocates cmap, sets fbops/fix/var, reserves the TC resource, maps MMIO, derives SFB and DAC pointers, maps framebuffer memory, reads `SFB_REG_VID_BASE` and offsets `screen_base` into the active video buffer, disables cursor, reads screen timing, measures oscillators, registers fbdev, grabs a device reference, and logs oscillator data. Remove unregisters, unmaps framebuffer/MMIO, releases resources, frees cmap, and releases `fb_info`.

State and persistence behavior: geometry and pixclock are derived from hardware registers at probe and then stored in `info->var`. Palette state lives in the Bt459. Oscillator readings are cached in `par->osc0`/`osc1`. No persistent storage exists. The active framebuffer base can be offset within SRAM depending on `VID_BASE`.

Dependencies and integration points: depends on TurboChannel bus speed APIs, fbdev default IOMEM ops, Linux delay/resource/ioremap APIs, and `<video/pmagb-b-fb.h>` register constants. Matching uses TC strings `DEC` and `PMAGB-BA`.

Risks: oscillator measurement uses polling loops and timing assumptions; inaccurate TC speed or stuck counters can skew pixclock. `screen_size` subtracts twice the `vid_base` offset, so unusual hardware values could underflow or reduce usable memory unexpectedly. The driver does not expose acceleration despite SFB hardware. Fixed 8-bpp pseudocolor operation limits mode flexibility. As with PMAG-BA, palette writes use old fbdev return conventions.

Test signals: probe on PMAGB-B hardware with different oscillator selections, verify decoded resolution/timings from SFB registers, colormap writes, framebuffer base offset handling, cursor disabled state, boot-option disable path, failure-path resource cleanup, and remove after active console use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/pmagb-b-fb.c -->
