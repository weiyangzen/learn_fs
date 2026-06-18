# Research Report: subset-b-005563

This grouped report covers the requested framebuffer sources under `sources/distributed-fs/ceph-client/drivers/video/fbdev/`. Each section is delimited for deterministic reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/macfb.c

Purpose: `macfb.c` is a simple boot-time framebuffer driver for classic Macintosh systems whose hardware modes are already established by firmware/bootloader and whose color-map programming is either model-specific or unknown. It does not perform mode setting; it maps the boot-provided framebuffer from `mac_bi_data`, builds `fb_info`/`fb_fix_screeninfo`/`fb_var_screeninfo`, optionally attaches a CLUT writer for the detected Mac video controller, allocates a colormap, and registers one fbdev.

Important APIs and functions: `macfb_init()` is the module init path. It consumes `fb_get_options("macfb")`, checks `MACH_IS_MAC`, derives resolution/depth/stride/address from `mac_bi_data`, maps `screen_base`, classifies the visual, detects NuBus display cards with `for_each_func_rsrc()`, and selects one of `dafb_setpalette()`, `v8_brazil_setpalette()`, `rbv_setpalette()`, `mdc_setpalette()`, `toby_setpalette()`, `jet_setpalette()`, `civic_setpalette()`, or `csc_setpalette()`. `macfb_setcolreg()` is the main fbops callback and either delegates indexed-color updates to the selected palette function or fills `pseudo_palette` for 16/24/32 bpp truecolor.

Control flow: initialization parses `inverse` and experimental `vidtest`, rejects unsupported models/depths, maps memory, sets timing placeholders for fbset compatibility, then performs a large model switch for internal video or NuBus card switch for add-in video. Palette updates are synchronous MMIO/NuBus register writes guarded with `local_irq_save()` to preserve register-write ordering. Failure unwinds colormap and I/O mappings.

State and persistence: state is static for the lifetime of the module: one global `fb_info`, global fix/var templates, one `pseudo_palette`, mapped CLUT register pointers, selected `macfb_setpalette`, and `slot_addr` for NuBus cards. There is no suspend/resume, hotplug, mode persistence, or runtime reprobe. DAFB additionally keeps a static `lastreg` cursor because that hardware cannot directly seek to arbitrary CLUT entries.

Dependencies and integration points: this file depends on m68k Macintosh boot info (`asm/macintosh.h`, `asm/setup.h`), NuBus accessors, fbdev core registration, and generic iomem fbops. It intentionally avoids the richer Mac mode library because the mode is already supplied by boot firmware. It coexists with more specific drivers by rejecting models handled elsewhere, notably Q630/P588 for `valkyriefb`.

Risks: the model table is hardware-knowledge-heavy and several entries are guesses or explicitly experimental. Palette functions assume register layouts and timing; wrong CLUT mapping can hang or corrupt display state. `macfb_init()` does not verify every `ioremap()` for CLUT register blocks before later palette use. The singleton static design also assumes only one active Mac framebuffer.

Test signals: useful validation is booting supported 68k Mac models at 1/2/4/8/16/24/32 bpp, confirming `/dev/fb0` registration, console rendering, `fbset` reporting, cmap updates through fbcon/X, and correct rejection of unsupported depths. Regression tests should watch boot logs for framebuffer address/mode, use palette cycling on indexed modes, and exercise module option parsing for `inverse` and `vidtest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.c

Purpose: `macmodes.c` is a small exported fbdev helper library that translates between legacy MacOS video mode/color mode numbers and Linux `fb_var_screeninfo`/`fb_videomode` structures. It also maps Macintosh monitor-sense values to default Mac mode IDs and lets Mac-specific users search a Mac mode database via `fb_find_mode()`.

Important APIs and functions: exported functions are `mac_vmode_to_var()`, `mac_var_to_vmode()`, `mac_map_monitor_sense()`, and `mac_find_mode()`. The file's core data is `mac_modedb[]`, ordered to match the named Mac timing comments, `mac_modes[]`, mapping VMODE constants to mode database entries, and `mac_monitors[]`, mapping monitor sense codes to VMODE constants with a catch-all fallback.

Control flow: `mac_vmode_to_var()` linearly finds a VMODE, clears the destination var, applies one of the supported CMODE layouts (8, 16/15-bit, or 32/24-bit), then copies timing fields from the selected `fb_videomode`. `mac_var_to_vmode()` infers CMODE from bits-per-pixel, searches the ordered mode map for matching or closest larger resolution/pixclock/vmode, and returns the chosen VMODE. `mac_map_monitor_sense()` is a simple lookup with a final default entry. `mac_find_mode()` switches to the Mac mode database only when the option string begins with `mac`; otherwise it delegates to the standard fbdev database.

State and persistence: all mode and monitor tables are immutable static data. The library has no mutable state, no hardware side effects, and no persistence beyond exported symbols available to linked/modules users.

Dependencies and integration points: it depends on Linux fbdev core structures and `fb_find_mode()`, and is included by Mac/PPC fbdev drivers through `macmodes.h`. `matroxfb_base.c` uses it on PowerMac builds to convert requested `vmode`/`cmode` or NVRAM-derived values into startup fb settings.

Risks: several interlaced modes are intentionally disabled because timings are unknown, but monitor-sense mappings still contain VMODE values for those modes; callers that pass them to `mac_vmode_to_var()` get `-EINVAL`. `mac_var_to_vmode()` relies on table ordering and has a suspicious inner-loop comparison against the earlier `mode->pixclock` rather than `clk_mode->pixclock`, so changes to ordering could alter matching behavior. The helper does no EDID validation.

Test signals: test by converting every defined non-disabled VMODE with CMODE_8/16/32 and back where possible, checking monitor-sense fallback behavior, and booting PowerMac fbdev users with `vmode:`/`cmode:` parameters. Edge tests should cover interlaced monitor sense values, mode strings with and without `mac` prefix, and var requests that exceed all known Mac modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.h

Purpose: `macmodes.h` defines the public contract for the MacOS video mode helper library. It provides the legacy VMODE and CMODE numeric constants used by Macintosh firmware/NVRAM and fbdev drivers, declares conversion/search helpers, and records NVRAM offsets used for default video mode and color mode.

Important APIs and types: the header declares `mac_vmode_to_var()`, `mac_var_to_vmode()`, `mac_map_monitor_sense()`, and `mac_find_mode()`. It defines VMODE values from `VMODE_NVRAM` through `VMODE_1600_1024_60`, plus `VMODE_MAX` and `VMODE_CHOOSE`. It defines CMODE sentinel values (`CMODE_NVRAM`, `CMODE_CHOOSE`) and supported color modes (`CMODE_8`, `CMODE_16`, `CMODE_32`). `NV_VMODE` and `NV_CMODE` are fixed NVRAM offsets.

Control flow: this file has no executable flow; it constrains callers to the constants and prototypes implemented in `macmodes.c`. Compile-time inclusion lets drivers build mode-selection flows without duplicating Apple numeric IDs.

State and persistence: the only persistence-related content is the NVRAM address constants. The header does not read or write NVRAM itself; that is done by users such as `matroxfb_base.c` on PowerMac builds.

Dependencies and integration points: it expects callers to include or otherwise know `struct fb_var_screeninfo` and `struct fb_info`. It is included from `matroxfb_base.h` when `CONFIG_PPC_PMAC` is set and can be consumed by other Mac framebuffer drivers.

Risks: constants must remain synchronized with Apple mode numbers and with the lookup tables in `macmodes.c`; adding a VMODE here without updating the implementation can create accepted build-time values that fail at runtime. The CMODE naming is historical: CMODE_16 is documented as actually 15 bits/pixel and CMODE_32 as actually 24 bits/pixel plus padding/alpha, which can confuse users expecting generic fbdev depth semantics.

Test signals: compile all users under `CONFIG_PPC_PMAC`, verify NVRAM-derived mode selection paths, and ensure every public VMODE intended to work has a corresponding `mac_modes[]` entry. Header-level regression checks are mostly build and ABI checks: no duplicate constants, unchanged exported prototypes, and matching `VMODE_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/Makefile -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/Makefile

Purpose: this Makefile wires the Matrox fbdev driver family into Kbuild. It selects the always-required core objects for `CONFIG_FB_MATROX` and conditionally adds G-series, I2C/DDC, MAVEN TV-out, CRTC2, and PLL support.

Important build rules: `my-obj-$(CONFIG_FB_MATROX_G)` adds `g450_pll.o`, `matroxfb_g450.o`, and `matroxfb_crtc2.o` for G-series hardware. `obj-$(CONFIG_FB_MATROX)` builds the main driver objects: `matroxfb_base.o`, `matroxfb_accel.o`, `matroxfb_DAC1064.o`, `matroxfb_Ti3026.o`, `matroxfb_misc.o`, and any enabled `my-obj-y`. `obj-$(CONFIG_FB_MATROX_I2C)` builds `i2c-matroxfb.o`. `obj-$(CONFIG_FB_MATROX_MAVEN)` builds `matroxfb_maven.o` and `matroxfb_crtc2.o`.

Control flow: Kbuild evaluates config-dependent lists and links the selected objects as built-in or module objects according to the parent Kconfig choices. There is no runtime behavior in the Makefile, but it determines which exported symbols and module init functions exist.

State and persistence: no runtime state. The key persistence implication is link composition: enabling MAVEN or G-series can include `matroxfb_crtc2.o`, creating a secondary fbdev extension module/path in addition to the base device.

Dependencies and integration points: the object list reflects internal symbol dependencies: `matroxfb_base.o` needs the low-level switch exports from DAC files, `g450_pll.o` is used by G450/G550 code, `i2c-matroxfb.o` registers through `matroxfb_register_driver()`, and MAVEN/CRTC2 pieces depend on the base Matrox extension-driver API.

Risks: `matroxfb_crtc2.o` appears in both G and MAVEN conditionals; Kbuild normally handles duplicate object names in built-in lists, but configuration changes should be checked for duplicate-link warnings. Missing one of the low-level objects under a config option would surface as unresolved symbols or disabled hardware support.

Test signals: build matrix tests are the main signal: `CONFIG_FB_MATROX` alone, plus combinations with `CONFIG_FB_MATROX_G`, `CONFIG_FB_MATROX_I2C`, and `CONFIG_FB_MATROX_MAVEN` as built-in and modules. Inspect generated modules for expected `matroxfb`, `i2c-matroxfb`, MAVEN, and CRTC2 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.c

Purpose: `g450_pll.c` implements clock synthesis and programming for Matrox G450/G550 PLLs. It converts packed MNP values to frequencies, searches candidate divider settings for target output clocks, tests hardware lock stability, caches working settings, and programs pixel/system/video PLL registers through the DAC1064 accessors.

Important APIs and functions: exported functions are `matroxfb_g450_setclk()`, `g450_mnp2f()`, and `matroxfb_g450_setpll_cond()`. Internal helpers include `g450_firstpll()`/`g450_nextpll()` for candidate enumeration, `g450_setpll()` and `g450_cmppll()` for hardware register writes/compare, `g450_isplllocked()`/`g450_testpll()` for lock testing, `g450_findworkingpll()` for robustness scanning, and the small LRU-like cache helpers `g450_addcache()`/`g450_checkcache()`.

Control flow: `matroxfb_g450_setclk()` allocates a candidate/delta table and calls `__g450_setclk()`. The latter prepares clock source/power state based on PLL type, selects the relevant limits/cache, enumerates MNP candidates sorted by frequency delta, reuses a cached known-good setting if available, otherwise probes nearby loop-control variants and lock status, writes the selected MNP, updates `minfo->hw.DACclk` for system PLL, and returns the programmed MNP.

State and persistence: persistent driver state is stored in `minfo->cache.{pixel,system,video}` and `minfo->hw.DACclk`. Hardware state persists in DAC PLL registers and PCI option registers. The cache keys mask frequency-significant bits to allow reuse of lock-stable MNP variants across calls.

Dependencies and integration points: this file depends on `matroxfb_base.h` for `matrox_fb_info`, PLL limits/features, PCI/MMIO helpers, and lock macros; it depends on `matroxfb_DAC1064.h` for DAC register constants and DAC I/O. DAC1064/G450 output code calls it when computing clocks for CRTC1/CRTC2, video PLL, legacy VGA clocks, and system memory clocks.

Risks: PLL programming can blank displays or lock hardware if sequencing is wrong. Candidate enumeration assumes table size 64 is larger than all possible M/P combinations. Several register writes are chipset-specific and comments note PC breakage for one DVI clock register. Lock testing is polling-heavy and can add latency. Incorrect PLL limits from BIOS/PINS parsing can produce unstable clocks.

Test signals: validate by setting a range of CRTC1 and CRTC2 modes on G450/G550, checking no PLL lock timeout, stable display, and accurate `g450_mnp2f()` frequency reporting. Exercise cache hits by switching between modes repeatedly. Regression tests should include system/video PLL setup during cold initialization and DVI/panel-link scenarios near `max_pixel_clock_panellink`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.h

Purpose: `g450_pll.h` exposes the G450/G550 PLL helper interface to other Matrox fbdev modules. It is intentionally small: include the base driver state definition and declare the three public PLL helpers implemented in `g450_pll.c`.

Important APIs: `matroxfb_g450_setclk()` computes, tests, caches, and programs a target clock for a selected PLL. `g450_mnp2f()` converts a packed MNP register value to an output frequency using `minfo->features.pll.ref_freq`. `matroxfb_g450_setpll_cond()` writes a packed MNP only when the target PLL does not already contain it.

Control flow: no executable flow in the header. It provides compile-time declarations for DAC1064/G450 code paths to call during preinit, mode computation, and output restore.

State and persistence: the header itself owns no state. Its functions operate on `struct matrox_fb_info`, so callers must have initialized PLL feature limits, caches, DAC locks, and PCI/MMIO mappings before use.

Dependencies and integration points: it includes `matroxfb_base.h`, which makes it part of the same internal Matrox driver ABI. It is used by `matroxfb_DAC1064.c` and likely G450-specific support objects selected by the Makefile.

Risks: callers can request invalid PLL IDs or use uninitialized `matrox_fb_info` fields; implementation returns errors for invalid IDs but hardware sequencing still relies on correct caller context. Because the header is not a stable external API, symbol or signature changes require coordinated updates in all Matrox objects.

Test signals: build all `CONFIG_FB_MATROX_G` configurations and load/use G450/G550 modes. Static checks should ensure prototypes match exported symbols and no non-G configs include this header without required object linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/i2c-matroxfb.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/i2c-matroxfb.c

Purpose: `i2c-matroxfb.c` is an extension module that provides bit-banged I2C adapters for Matrox framebuffer devices. It exposes primary DDC, optional secondary DDC, and optional MAVEN TV-out buses over GPIO bits in the DAC general I/O registers.

Important APIs and functions: it implements a private `matroxfb_driver` named `i2c-matroxfb` with `i2c_matroxfb_probe()` and `i2c_matroxfb_remove()`, registered via exported `matroxfb_register_driver()`. GPIO/I2C callbacks are `matroxfb_gpio_setsda()`, `matroxfb_gpio_setscl()`, `matroxfb_gpio_getsda()`, and `matroxfb_gpio_getscl()` through an `i2c_algo_bit_data` template. `i2c_bus_reg()` initializes each `i2c_bit_adapter`.

Control flow: module init registers the extension driver. For each existing or future Matrox fbdev instance, probe allocates `matroxfb_dh_maven_info`, initializes DAC GPIO registers under DAC lock, registers the primary DDC adapter with Millennium-specific or generic bit masks, and on dual-head devices attempts secondary DDC and MAVEN adapters. If the MAVEN bus registers, it scans address `0x1b` for a `maven` client. Remove unregisters any initialized adapters and frees state.

State and persistence: per-device state is `matroxfb_dh_maven_info`, containing three `i2c_bit_adapter` structures. Hardware GPIO direction/data registers are reset during probe. Adapter registration persists in the kernel I2C core until remove.

Dependencies and integration points: depends on Matrox DAC I/O helpers/locks, `matroxfb_maven.h` for `i2c_bit_adapter`, Linux I2C bit-banging core, and the Matrox private extension-driver list. Consumers include EDID/DDC code and the MAVEN encoder driver.

Risks: GPIO register access shares DAC registers with other code and XFree/Xorg-era users, so `matroxfb_set_gpio()` repeatedly resets `GENIODATA`. Secondary DDC failure is partially tolerated, but primary failure aborts probe. The bit-banged bus has fixed delay/timeout values and may be fragile on unusual cards or cable states. The code treats `-ENODEV` on secondary DDC as a VGA-to-TV plug hint.

Test signals: load with `CONFIG_FB_MATROX_I2C` on Millennium, G200/G400, and dual-head cards; verify `/sys` I2C adapters named `DDC:fb%u #0`, `DDC:fb%u #1`, and `MAVEN:fb%u`; read EDID on primary/secondary connectors; and confirm module unload removes adapters cleanly. Watch dmesg for tolerated secondary/MAVEN registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/i2c-matroxfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.c

Purpose: `matroxfb_DAC1064.c` is the low-level RAMDAC/output driver for Matrox Mystique and G-series devices that use the MGA1064/DAC1064-compatible DAC family, including G100/G200/G400 and G450/G550-specific output handling. It supplies `matrox_switch` implementations used by the base PCI driver for preinit, reset, mode init, and restore.

Important APIs and functions: exported switch instances are `matrox_mystique` and `matrox_G100` when enabled. Shared exported helpers are `DAC1064_global_init()` and `DAC1064_global_restore()`. Important internals include `DAC1064_calcclock()`, `DAC1064_setpclk()`, `DAC1064_setmclk()`, `DAC1064_init_1()`/`DAC1064_init_2()`, `DAC1064_restore_1()`/`DAC1064_restore_2()`, `MGA1064_preinit()`/`reset()`/`init()`/`restore()`, `MGAG100_preinit()`/`reset()`/`init()`/`restore()`, and G450-specific `g450_set_plls()`, `g450_preinit()`, clock and memory init helpers.

Control flow: preinit sets chip capabilities, output routing, PLL feature limits, PCI option registers, memory interface defaults, and output descriptors. Reset programs memory/system clocks and device-specific defaults. Init builds DAC register images for the requested bpp and sync mode, calls VGA CRTC initialization, and populates palette defaults. Restore writes PCI, DAC, VGA, and CRTC extension registers back to hardware. For G450/G550, output routing also selects pixel/video/reference PLLs and power bits for DAC, secondary, and DVI outputs.

State and persistence: hardware images live in `minfo->hw.DACreg`, `DACclk`, `DACpal`, `MXoptionReg`, CRTC arrays, and G450 `crtc2.ctl`. Persistent device facts and BIOS-derived values live in `minfo->features`, `values`, `devflags`, `outputs`, and PLL caches. Hardware state persists in PCI option registers, DAC extended registers, memory timing registers, and PLLs.

Dependencies and integration points: depends on `matroxfb_misc` for generic VGA timing/PLL calculation and PINS parsing results, `matroxfb_accel` for later accelerated fbops, `g450_pll` for G450/G550 PLL programming, and `linux/matroxfb.h` for output mode constants. The base driver invokes the switch hooks during PCI initialization and every primary-head mode set; CRTC2 code calls global DAC init/restore when secondary routing changes.

Risks: this is highly hardware-sequenced code. Comments warn that accessing the device while MCLK is stopped can lock the PCI bus. G450/G550 memory and PLL initialization depends on BIOS/PINS values and has many chipset-specific magic registers. Output routing has tricky interactions between DAC, MAVEN, panel-link, TMDS, pixel PLL, and video PLL. Failure modes include blank display, unstable clocks, broken acceleration, or bus lockups.

Test signals: test cold boot and mode switches across Mystique, G100, G200, G400, G450, and G550 configs. Watch for PLL lock errors, memory-size stability, correct palette at 8/16/24/32 bpp, working primary/secondary output routing, and no PCI hangs with `init`/`noinit` options. G450/G550 should be tested with monitor, TV/MAVEN, and DVI/panel-link combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.h

Purpose: `matroxfb_DAC1064.h` defines the internal interface and register map for MGA1064/DAC1064-compatible Matrox RAMDACs. It exposes low-level switch objects and global DAC helper functions while centralizing DAC register numbers, bit definitions, and software positions into `matrox_hw_state.DACreg`.

Important APIs and types: it declares `matrox_mystique`, `matrox_G100`, `DAC1064_global_init()`, and `DAC1064_global_restore()` behind configuration guards. Register definitions cover palette access, hardware cursor, DVI clock control, pixel/system/video PLL registers, general control, misc/output connection/power/pan mode registers, and `enum POS1064` indexes used by DAC register image arrays.

Control flow: no executable flow. The header's register constants are consumed by DAC1064, G450 PLL, I2C, and related output code when building or writing hardware state.

State and persistence: the header maps logical names to persistent hardware state in DAC registers and to cached software state positions. `POS1064_*` enum values must align with the arrays in `matroxfb_DAC1064.c`; any mismatch corrupts restore programming.

Dependencies and integration points: includes `matroxfb_base.h`, binding it to `struct matrox_fb_info`, `matrox_switch`, and common register accessors. It is an internal driver ABI for Matrox fbdev objects, not a user-visible header.

Risks: the header contains many chipset-specific bit definitions with overlapping meanings across G200/G400/G450. Wrong bit use can power down outputs, select the wrong PLL, or disable the LUT. Because several definitions share numeric registers with different names, future changes need hardware-family awareness.

Test signals: build all `CONFIG_FB_MATROX_MYSTIQUE` and `CONFIG_FB_MATROX_G` combinations. Runtime smoke tests should verify every register-image index used by `MGA1064_DAC_regs[]` maps to the expected `POS1064_*` position, and that G450/G550 DVI/secondary output paths still program `XOUTPUTCONN`, `XPWRCTRL`, and `XPANMODE` correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.c

Purpose: `matroxfb_Ti3026.c` is the low-level RAMDAC driver for Matrox Millennium/Millennium II boards using the TI TVP3026 RAMDAC. It provides the `matrox_millennium` switch used by the base Matrox PCI driver for setup, clocking, mode programming, and restore.

Important APIs and functions: the exported object is `matrox_millennium`. Internal functions include `Ti3026_calcclock()` for TVP3026 PLL encoding, `Ti3026_setpclk()` for pixel/loop PLL state calculation, `Ti3026_init()` for DAC/VGA register image construction, `ti3026_setMCLK()` for memory clock programming through a temporary pixel-clock path, `ti3026_ramdac_init()`, `Ti3026_restore()`, `Ti3026_reset()`, and `Ti3026_preinit()`. Register constants define palette, cursor, latch, mux, clock, PLL, color-key, and misc control registers.

Control flow: preinit identifies Millennium generation, sets capabilities, output descriptors, PCI option register bits, reads RAMDAC revision, stops DAC clocks, resets VGA-ish state, and resets the accelerator. Reset initializes PLL feature limits and MCLK unless `noinit`. Init chooses register images for 4/8/16/24/32 bpp, initializes VGA timing, adjusts sync/cursor/interleave settings, and calculates pixel/loop PLL bytes. Restore writes PCI, VGA, CRTC extension, DAC control, pixel PLL, and loop PLL registers, waiting for PLL lock when needed.

State and persistence: software state is stored in `minfo->hw.DACreg`, `DACclk`, `MXoptionReg`, `CRTCEXT`, and `minfo->accel.ramdac_rev`, plus capability flags such as `millenium`, `milleniumII`, `interleave`, and `cfb4`. Hardware state persists in TVP3026 extended registers, PLLs, PCI option register, and Matrox accelerator reset/memory registers.

Dependencies and integration points: depends on `matroxfb_base.h` for device state and MMIO/PCI helpers, `matroxfb_misc` for generic VGA/PLL calculations, `matroxfb_accel` for capability interplay, and `linux/matroxfb.h` for output mode constants. The base driver invokes this file through `hw_switch` for Millennium device IDs.

Risks: clock programming is slow and heavily sequenced; the code waits up to roughly five seconds for several PLL lock paths. `ti3026_setMCLK()` temporarily repurposes pixel PLL output for MCLK, so interruption or wrong register order can destabilize display memory. 24 bpp handling has RAMDAC revision and interleave-specific workarounds plus an `inv24` option. Many bit settings are historical magic values.

Test signals: validate Millennium and Millennium II with 4/8/15/16/24/32 bpp modes, interleaved and non-interleaved memory sizes, and repeated mode switches. Watch for pixel/loop/memory PLL timeout messages, correct hardware cursor blanking, stable acceleration after reset, and correct palette/directcolor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.h

Purpose: `matroxfb_Ti3026.h` is the minimal internal header for the Millennium TVP3026 low-level driver. It declares the `matrox_millennium` switch when Millennium support is enabled.

Important APIs: `extern struct matrox_switch matrox_millennium` is the sole public symbol declaration, guarded by `CONFIG_FB_MATROX_MILLENIUM`. The switch supplies `preinit`, `reset`, `init`, and `restore` callbacks to the base driver.

Control flow: no runtime flow. Inclusion lets `matroxfb_base.c` reference the Millennium switch in board tables when the configuration includes Millennium support.

State and persistence: no state is owned by the header. All state is carried through `struct matrox_fb_info` and programmed by `matroxfb_Ti3026.c`.

Dependencies and integration points: includes `matroxfb_base.h`, so the switch type and shared device state are available. It is part of the internal Matrox fbdev object linkage selected by Kbuild.

Risks: if the config guard or object list changes inconsistently, Millennium board-table entries can fail to compile or link. The header intentionally does not expose TVP3026 register constants; consumers should not bypass the switch abstraction.

Test signals: build with and without `CONFIG_FB_MATROX_MILLENIUM`; confirm `matroxfb_base.c` device tables resolve `matrox_millennium` only when expected. Runtime signals are covered by the C file through successful Millennium probe and mode restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.c

Purpose: `matroxfb_accel.c` installs and implements accelerated fbdev drawing operations for Matrox framebuffer devices. It configures accelerator pixel format registers and replaces generic cfb operations with hardware-backed copyarea, fillrect, and 1 bpp imageblit paths when text acceleration is enabled.

Important APIs and functions: exported `matrox_cfbX_init()` selects fbops and writes accelerator setup registers (`M_PITCH`, `M_YDSTORG`, `M_OPMODE`, `M_MACCESS`, etc.) based on current bpp. Internal accelerated operations include `matrox_accel_bmove()`, `matrox_accel_bmove_lin()`, `matroxfb_copyarea()`, `matroxfb_cfb4_copyarea()`, `matroxfb_accel_clear()`, `matroxfb_fillrect()`, `matroxfb_cfb4_clear()`, `matroxfb_cfb4_fillrect()`, `matroxfb_1bpp_imageblit()`, and `matroxfb_imageblit()`.

Control flow: mode setting in `matroxfb_base.c` calls `matrox_cfbX_init()` after registers are restored. The function starts with generic cfb fallbacks, computes Matrox access/opmode/pitch for bpp, optionally enables accelerated callbacks, and records accelerator state in `minfo->accel`. fbdev operations then program drawing registers, wait for FIFO/idle, and fall back to software when unsupported (for example odd 4 bpp copy boundaries or non-1bpp imageblit).

State and persistence: persistent software state is `minfo->accel.{m_dwg_rect,m_opmode,m_access,m_pitch}` and bpp-dependent pseudo-palette values in `minfo->cmap`. Hardware state is the drawing engine registers and FIFO/idle state. The optional `MATROXFB_USE_SPINLOCKS` path can serialize accelerator access through `minfo->lock.accel`.

Dependencies and integration points: depends on Matrox MMIO register macros from `matroxfb_base.h`, DAC-family flags such as Millennium II transparency behavior, generic fbdev cfb helpers, and unaligned/MMIO copy helpers. It is called by the base driver after each primary-head mode change.

Risks: accelerator register programming is sensitive to pitch, bpp, interleave, endian opmode, and YDSTORG. Several operations busy-wait with `WaitTillIdle()`. 4 bpp handling mixes accelerated byte-aligned middle spans with direct framebuffer read/modify/write edges. Imageblit comments note that fbdev logo code can pass misleading depth, so non-1bpp is intentionally software.

Test signals: run fbcon text scrolling, rectangle fills, area copies, and monochrome glyph rendering at 4/8/15/16/24/32 bpp with acceleration on/off. Verify no corruption when panning changes YDSTORG, with odd 4 bpp coordinates, and on big-endian platforms. Watch for hangs in FIFO/idle loops during stress scrolling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.h

Purpose: `matroxfb_accel.h` declares the Matrox acceleration initializer used by the base mode-setting path.

Important APIs: `matrox_cfbX_init(struct matrox_fb_info *minfo)` configures accelerator registers and fbops for the current framebuffer var. It is implemented in `matroxfb_accel.c`.

Control flow: no executable flow in the header. The base driver includes it and calls the function after mode programming so copy/fill/image operations match the new bpp and pitch.

State and persistence: no state is owned here. The declared function mutates `minfo->fbops`, `minfo->accel`, and hardware drawing registers.

Dependencies and integration points: includes `matroxfb_base.h` for `struct matrox_fb_info`. It is part of the core `CONFIG_FB_MATROX` object set, so the declaration should always resolve when the base driver is built.

Risks: if callers invoke the initializer before `fbcon.var`, `curr.ydstorg`, MMIO mappings, and capability flags are valid, it can program wrong accelerator state. The header offers no additional type abstraction, so it assumes internal Matrox driver ordering discipline.

Test signals: build core Matrox configs and exercise mode switches that call `matrox_cfbX_init()`. Runtime behavior should show correct fbops selection when `FB_ACCELF_TEXT` is toggled and safe fallback to cfb helpers when acceleration is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.c

Purpose: `matroxfb_base.c` is the central PCI/fbdev driver for Matrox Millennium, Mystique, G100, G200, G400, G450, and G550 cards. It handles module/boot parameters, PCI probe/remove, BAR mapping, VRAM detection, fbdev registration, primary-head mode validation/programming, pan/blank/ioctl operations, IRQ/vsync handling, and a private extension-driver registry used by I2C/MAVEN/CRTC2 modules.

Important APIs and functions: public/exported helpers include `matroxfb_register_driver()`, `matroxfb_unregister_driver()`, `matroxfb_wait_for_sync()`, and `matroxfb_enable_irq()`. Main probe/setup flow is `matroxfb_probe()` -> `initMatrox2()` -> `register_framebuffer()` and `matroxfb_register_device()`. fbops include `matroxfb_open()`, `release()`, `check_var()`, `set_par()`, `setcolreg()`, `pan_display()`, `blank()`, and `ioctl()`. Device tables are `dev_list[]` and `matroxfb_devices[]`; board capability templates point at low-level `matrox_switch` implementations.

Control flow: initialization parses parameters into global defaults, registers a PCI driver, and matches supported Matrox IDs/subsystems. Probe removes conflicting apertures, enables PCI, allocates `matrox_fb_info`, sets devflags, initializes locks/waitqueues, and calls `initMatrox2()`. That function maps MMIO and framebuffer BARs, adjusts PCI options, reads BIOS/PINS, calls low-level preinit/reset, detects memory, applies MTRR/WC, prepares default mode from VESA or Mac vmode/cmode, registers fbdev, and forces initial hardware programming if needed. `matroxfb_set_par()` validates var, computes timings, lets active outputs compute clocks, invokes low-level init/restore, programs panning registers, starts outputs, and initializes acceleration.

State and persistence: per-card state lives in `struct matrox_fb_info`: fbdev object, current mode, hardware register image, PCI/MMIO/video mappings, IRQ state, vsync counters, output routing, PLL limits/caches, BIOS/PINS values, capabilities, devflags, pseudo-palette, and extension-driver data. Global module parameters persist across probes and are partially consumed/mutated for multihead behavior (`dev`, `novga`, `nobios`, `noinit`, `outputs`). Hardware state persists in PCI config, VGA/DAC/CRTC/accelerator registers, and mapped VRAM.

Dependencies and integration points: depends on fbdev core, PCI core, aperture conflict removal, arch write-combining helpers, Matrox misc/DAC/Ti/G450/MAVEN/CRTC2 helpers, Linux matroxfb ioctls, V4L2 control structs for TV-out controls, and Mac mode helpers on PowerMac. Extension modules attach via the private `matroxfb_driver_list`.

Risks: this is old hardware-control code with many global parameters and magic register sequences. Removal defers cleanup while users hold the fb, but lifetime protection is not modern refcounting. IRQ enable/disable is shared between primary and CRTC2 vsync waits. VRAM probing writes test patterns into mapped video memory. Mode validation mutates user vars to fit hardware rather than always failing. Output-routing ioctls can reprogram clocks and shared outputs while secondary head exists.

Test signals: build and boot each supported config family, verify probe logs, memory size detection, fbdev registration, mode set, pan, blank, palette updates, vblank ioctls, `FBIO_WAITFORVSYNC`, module unload, and hotplug/remove where possible. Parameter tests should cover `noaccel`, `nopan`, `mem`, `vesa`, custom timings, `outputs`, `dfp`, PowerMac `vmode/cmode`, and multi-adapter `dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.h

Purpose: `matroxfb_base.h` is the core internal header for the Matrox fbdev driver family. It defines debug controls, MMIO helpers, timing/PLL/output/state structures, the main `matrox_fb_info` object, the low-level switch interface, extension-driver API, register constants, endian-dependent accelerator opmodes, lock macros, and exported base helpers.

Important APIs and types: key types are `vaddr_t`, `my_timming`, `matrox_pll_cache`, `matrox_pll_limits`, `matrox_pll_features`, `matrox_hw_state`, `matrox_accel_data`, `matrox_altout`, `matrox_bios`, `matrox_vsync`, `matrox_fb_info`, `matrox_switch`, and `matroxfb_driver`. Important inline helpers wrap `readb/writeb/readl/writel`, `mga_memcpy_toio()`, and virtual address arithmetic. Register constants cover drawing engine, VGA, DAC, interrupt, CRTC2, and PCI option registers.

Control flow: no full runtime flow, but macros and inlines define how all Matrox modules perform MMIO, wait for FIFO/idle, lock DAC/accelerator sections, and access `matrox_fb_info` from `fb_info`. `matrox_switch` formalizes the preinit/reset/init/restore lifecycle used by the base driver.

State and persistence: the header describes nearly all persistent per-device state. `matrox_fb_info` contains live fbdev state, hardware shadow registers, PCI device, vsync wait queues/counters, output routing, registered extension modules, video/MMIO mappings, feature limits, locks, chip/capability/devflag state, BIOS/PINS data, PLL caches, G450 register values, and a 16-entry pseudo-palette.

Dependencies and integration points: includes broad kernel subsystems: fbdev, PCI, console/selection, timers, spinlocks, I/O, unaligned access, and optional PowerMac `macmodes.h`. Every Matrox source in this subset includes it directly or indirectly, making it the internal ABI boundary.

Risks: because this header exposes hardware registers and full mutable state to all modules, invariants are convention-based. Some macros are busy-wait loops without timeouts (`mga_fifo`, `WaitTillIdle`). Optional spinlock protection is compile-time disabled by default. Endian opmode handling has TODOs for some bpp combinations. Layout changes to `matrox_fb_info` affect extension modules that store pointers and call back into base fbops.

Test signals: compile all Matrox config combinations on little- and big-endian targets, with and without Millennium/G/Mystique/I2C/MAVEN. Runtime tests should stress MMIO wrappers, acceleration idle waits, DAC locking under concurrent mode/palette/I2C activity, and extension-driver registration/removal. Static analysis should flag direct hardware access that bypasses required locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.c

Purpose: `matroxfb_crtc2.c` implements the optional secondary framebuffer for Matrox G400/G450/G550-style CRTC2 hardware. It registers as a private Matrox extension driver, reserves or borrows a slice of VRAM for the second head, registers a second fbdev, and programs CRTC2 timing/output registers for 16/32 bpp display.

Important APIs and functions: extension entry points are `matroxfb_crtc2_probe()` and `matroxfb_crtc2_remove()` in a `matroxfb_driver` named `Matrox G400 CRTC2`. fbops are `matroxfb_dh_open()`, `release()`, `check_var()`, `set_par()`, `setcolreg()`, `pan_display()`, `blank()`, and `ioctl()`. Hardware helpers include `matroxfb_dh_restore()`, `matroxfb_dh_disable()`, `matroxfb_dh_pan_var()`, `matroxfb_dh_decode_var()`, and `matroxfb_dh_get_vblank()`.

Control flow: module init checks `fb_get_options("matrox_crtc2fb")` and registers the extension. Probe requires `minfo->devflags.crtc2`, allocates `matroxfb_dh_fb_info`, reserves the requested memory size from the top of VRAM or borrows from primary usable memory, initializes fix/cmap/fbops, registers a secondary framebuffer, and stores it in `minfo->crtc2.info` under lock. Mode setting validates 16/32 bpp, computes timings via `matroxfb_var2my()`, lets all outputs routed to CRTC2 compute clocks, programs CRTC2 registers or disables it, refreshes DAC1064 global state, and starts routed outputs.

State and persistence: secondary state is `matroxfb_dh_fb_info`, including its own `fb_info`, registration/initialized flags, pointer to primary `matrox_fb_info`, video offset/base/length/borrowed bytes, shared MMIO mapping, interlace flag, and 16-entry pseudo-palette. Primary state updated includes `minfo->crtc2.info`, `crtc2.pixclock`, `crtc2.mnp`, `hw.crtc2.ctl`, output routing, and vsync counter.

Dependencies and integration points: depends on the base Matrox extension API, `matroxfb_misc` timing conversion, DAC1064 global output helpers, MAVEN/output mode definitions, fbdev core, and user ioctl definitions in `linux/matroxfb.h`. Primary and secondary heads coordinate through shared output routing and shared VRAM/MMIO.

Risks: CRTC2 supports only 16 and 32 bpp here; invalid memory reservation or primary/secondary incompatible panning can break display. The module mutates primary `video.len_usable` when borrowing memory and restores it on deregister, so unload ordering matters. Output routing ioctls must reject conflicts with primary and panel-link constraints. Blank is effectively unimplemented. Register programming uses raw addresses and timing truncation to 8-pixel horizontal granularity.

Test signals: load with `matrox_crtc2fb` enabled on CRTC2-capable hardware, verify second fb registration, memory reservation size, 16/32 bpp mode setting, panning, vblank and wait-for-vsync ioctls, CRTC2 output routing to secondary/DAC/TV as available, and clean unload restoring primary usable memory. Test conflicts with DFP/panel-link and primary output ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.h

Purpose: `matroxfb_crtc2.h` defines the private secondary-head framebuffer state used by `matroxfb_crtc2.c`.

Important APIs and types: the main type is `struct matroxfb_dh_fb_info`. It contains a standalone `struct fb_info`, registration/initialization flags, a pointer to the primary `struct matrox_fb_info`, a video-memory descriptor with physical/virtual base, length, usable length, maximum length, offset from primary VRAM, and borrowed byte count, a shared MMIO descriptor, an `interlaced` bit, and a 16-entry pseudo-palette.

Control flow: no executable flow. The structure layout enables CRTC2 fbops to act like a separate fbdev while delegating lifetime, IRQ, output routing, and hardware access through the primary device.

State and persistence: this header defines all persistent per-secondary-fb software state. The `borrowed` field records how much primary usable VRAM was subtracted so deregistration can restore it. `offbase` is the hardware/programming link between the second fb's virtual screen and the shared physical framebuffer aperture.

Dependencies and integration points: includes `matroxfb_base.h` for `vaddr_t` and primary device state, plus `linux/ioctl.h`. `matroxfb_base.c` stores a pointer to this type opaquely in `minfo->crtc2.info`.

Risks: the structure shares MMIO and parent device lifetime rather than owning its own mappings, so stale secondary state after primary removal would be dangerous. Any layout changes must match `matroxfb_crtc2.c` assumptions around memory accounting, fbdev registration, and interlace panning.

Test signals: build with CRTC2 enabled, register/unregister secondary fb, and verify memory accounting fields through mode changes and module unload. Static checks should ensure no code treats the secondary `vbase` as independently iounmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_crtc2.h -->
