# subset-b-005567 Research

Grouped source research for OMAP2/3/4/5 fbdev DSS panel drivers, display registration/sysfs glue, the DSS apply compatibility layer, DISPC register programming, IRQ compatibility, and scaler coefficient tables. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sony-acx565akm.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sony-acx565akm.c

## Purpose

`panel-sony-acx565akm.c` is a SPI-controlled SDI panel driver for Sony ACX565AKM-compatible MIPI command panels used through the legacy OMAP DSS/fbdev display model. The complete 857-line source was read. It detects the LCD model over SPI, registers an `omap_dss_device`, proxies SDI connect/enable/timing operations to the upstream DSS output, and exposes backlight/CABC controls for panels that support them.

## Important APIs, Types, and Functions

The core state is `struct panel_drv_data`: embedded `omap_dss_device`, upstream `in` device, reset GPIO, SDI datapair count, current `omap_video_timings`, panel identity fields, brightness/CABC capability flags, sleep guard timing, SPI device, mutex, and `backlight_device`. SPI helpers are `acx565akm_transfer()`, `acx565akm_cmd()`, `acx565akm_write()`, and `acx565akm_read()`. Panel control is split across `panel_enabled()`, `panel_detect()`, `set_sleep_mode()`, `set_display_state()`, `acx565akm_panel_power_on()`, and `acx565akm_panel_power_off()`. Backlight integration uses `acx565akm_bl_ops`, `acx565akm_set_brightness()`, and CABC sysfs attributes `cabc_mode` and `cabc_available_modes`. DSS entry points are in `acx565akm_ops`.

## Control Flow

Probe requires a DT node, sets SPI mode 3, allocates driver data, finds the first endpoint source via `omapdss_of_find_source_for_first_ep()`, requests optional reset GPIO, waits after reset, reads display status and display ID, registers a backlight, creates CABC sysfs files when supported, initializes default 800x480 timings, and registers the display. Enable checks that the display is connected and inactive, then under `ddata->mutex` programs SDI timings/datapairs, enables the upstream SDI output, waits for panel timing requirements, deasserts reset according to the historical GPIO polarity quirk, exits sleep, turns display on, restores CABC, and updates brightness. Disable reverses display-on and sleep state, waits for two frames, asserts reset, and disables upstream SDI.

## State and Persistence Behavior

All state is volatile kernel driver state. `enabled`, `cabc_mode`, detected model/revision, brightness properties, and sleep guard jiffies persist only while the SPI device is bound. Hardware-visible state is held in panel registers and is restored during enable; CABC sysfs stores the requested CABC mode even when the panel is disabled and applies it on the next power-on. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on SPI, GPIO descriptors, backlight core, OF endpoint lookup, and `video/omapfb_dss.h`. It integrates with DSS as an SDI sink through `in->ops.sdi`, with fb/backlight through `backlight_device_register()`, and with sysfs through the backlight device kobject.

## Risks and Edge Cases

SPI transfers use 9-bit command/data framing and special 10-bit dummy handling for multi-byte reads, so controller support and endianness are critical. `acx565akm_transfer()` logs SPI failures but returns void, so many command failures are not propagated. The reset GPIO polarity comment documents compatibility with incorrect older DTS polarity. Remove unconditionally removes the CABC sysfs group even though it is created only when `has_cabc`, which is normally harmless but worth checking on sysfs changes. Sleep in/out timing relies on jiffies guards and fixed delays.

## Test Signals

Useful signals include DT probe with compatible `omapdss,sony,acx565akm`, SPI read of display ID/status, enable/disable cycling with SDI source connected, backlight brightness get/set, CABC sysfs read/write including unsupported modes, suspend/resume through DSS display disable/enable, and negative tests for missing endpoint, missing reset GPIO, unsupported SPI transfers, and unknown display ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-sony-acx565akm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td028ttec1.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td028ttec1.c

## Purpose

`panel-tpo-td028ttec1.c` is a SPI-initialized Toppoly TD028TTEC1 DPI panel driver for the legacy OMAP DSS/fbdev stack. The complete 476-line source was read. It provides fixed 480x640 timings, sends the JBT controller initialization sequence over 9-bit SPI, and registers a DPI `omap_dss_device`.

## Important APIs, Types, and Functions

`struct panel_drv_data` stores the embedded DSS device, upstream DPI source, data-line count, current timings, and SPI device. SPI programming helpers are `jbt_ret_write_0()`, `jbt_reg_write_1()`, and `jbt_reg_write_2()`, using `JBT_COMMAND` and `JBT_DATA` framing plus `enum jbt_register` register IDs. DSS driver callbacks are `td028ttec1_panel_connect()`, `disconnect()`, `enable()`, `disable()`, `set_timings()`, `get_timings()`, and `check_timings()`. Probe helpers are `td028ttec1_probe_of()` and `td028ttec1_panel_probe()`.

## Control Flow

Probe requires DT, configures SPI as 9 bits per word and mode 3, allocates state, finds the first endpoint source, sets default timings, fills an `omap_dss_device` with DPI type, and registers it. Enable validates connection and current state, programs optional DPI data lines and timings on the upstream source, enables the upstream DPI output, then sends the panel wake and register initialization sequence: three zero commands, deep standby exit, display interface setup, booster/power/gamma/timing registers, and finally `DISPLAY_ON`. Disable sends `DISPLAY_OFF`, output control and sleep/power-off commands, disables upstream DPI, and marks the DSS device disabled.

## State and Persistence Behavior

State is volatile and minimal: timings and SPI/upstream pointers live in `panel_drv_data`, while panel controller register state is reprogrammed on each enable. There is no sysfs state and no persistence across driver unbind or power loss.

## Dependencies and Integration Points

The driver depends on SPI and the OMAP DSS DPI operation table. It integrates with DT endpoint routing through `omapdss_of_find_source_for_first_ep()`, with DSS display enumeration via `omapdss_register_display()`, and with the SPI core via `module_spi_driver()`. It keeps old compatible strings and SPI IDs for DTB/module compatibility.

## Risks and Edge Cases

Initialization accumulates return values with `r |= ...`, so the final error is collapsed to `-EIO` and later SPI commands may still be attempted after an earlier failure. There is no local mutex around enable/disable or timing changes. `data_lines` is never populated from DT in this file, so it remains zero unless future code extends probe. The panel programming sequence is timing-sensitive and mostly fixed magic values.

## Test Signals

Signals include successful `spi_setup()` with 9-bit transfers, DT endpoint discovery, display registration, DPI enable followed by a visible image, error injection in SPI writes, disable/enable cycling, timing check delegation to the upstream DPI source, and compatibility matching for both `omapdss,tpo,td028ttec1` and older `omapdss,toppoly,td028ttec1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td028ttec1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td043mtea1.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td043mtea1.c

## Purpose

`panel-tpo-td043mtea1.c` is a SPI-controlled TPO TD043MTEA1 800x480 DPI panel driver. The complete 611-line source was read. It manages panel regulator/reset power sequencing, SPI register programming, gamma/mode/mirror sysfs controls, DSS DPI callbacks, and SPI device PM.

## Important APIs, Types, and Functions

`struct panel_drv_data` tracks the embedded `omap_dss_device`, upstream DPI source, video timings, data lines, SPI device, VCC regulator, reset GPIO, 12-entry gamma table, mode, mirror flags, and PM booleans. `tpo_td043_write()` encodes 16-bit SPI writes. Higher-level helpers are `tpo_td043_write_gamma()`, `tpo_td043_write_mirror()`, `tpo_td043_power_on()`, and `tpo_td043_power_off()`. Sysfs attributes expose `vmirror`, `mode`, and `gamma`. DSS callbacks in `tpo_td043_ops` handle connect, enable, disable, timing, and horizontal mirror operations. PM callbacks are `tpo_td043_spi_suspend()` and `tpo_td043_spi_resume()`.

## Control Flow

Probe configures SPI mode 0/16-bit words, allocates state, finds the endpoint source, loads default 800x480 mode and gamma table, obtains the `vcc` regulator and reset GPIO, creates panel sysfs attributes, initializes the DSS device, and registers the display. Enable programs optional DPI data lines and timings, enables the upstream DPI output, and powers/programs the panel unless the SPI device is suspended. Power-on enables the regulator, waits 160 ms, releases reset, writes mode, normal power register, PWM-related registers, mirror state, and gamma table. Disable turns off the upstream DPI output and powers the panel off unless SPI is suspended.

## State and Persistence Behavior

Gamma, mode, mirror flags, `powered_on`, `spi_suspended`, and `power_on_resume` are volatile runtime state. Sysfs writes update the in-memory desired state and immediately program hardware. Suspend records whether the panel was powered, powers it off, and restores it in SPI resume when needed. There is no persistent storage beyond hardware registers while powered.

## Dependencies and Integration Points

The file depends on SPI, regulator, GPIO descriptor, sysfs, PM sleep helpers, and OMAP DSS DPI operations. It integrates with DSS through `omapdss_register_display()`, `in->ops.dpi`, `set_mirror`/`get_mirror` callbacks, and DT compatible `omapdss,tpo,td043mtea1`.

## Risks and Edge Cases

The sysfs gamma parser accepts 12 unsigned integers but does not bound them to 10-bit values before truncating during SPI writes. Sysfs mode validates only three bits. Several SPI writes in power-on are not checked after the regulator is enabled, so partial programming can still set `powered_on`. Suspend/resume carefully handles the case where DSS enable happens before SPI clocks are available, but races with sysfs writes are not serialized by a mutex.

## Test Signals

Signals include regulator/reset sequencing, sysfs read/write for `vmirror`, `mode`, and `gamma`, SPI write failure paths, DPI enable/disable with visible output, suspend/resume while active and inactive, mirror callback behavior through DSS, and cleanup verifying sysfs group removal and upstream DSS reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td043mtea1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Kconfig

## Purpose

`dss/Kconfig` defines configuration symbols for the legacy OMAP2 DSS fbdev subsystem. The complete 111-line file was read. It selects required helpers, exposes optional debug/debugfs/IRQ-stat features, and gates hardware output blocks such as DPI, VENC, SDI, DSI, and HDMI variants.

## Important APIs, Types, and Functions

Important symbols include `FB_OMAP2_DSS_INIT`, `FB_OMAP2_DSS`, `FB_OMAP2_DSS_DEBUG`, `FB_OMAP2_DSS_DEBUGFS`, `FB_OMAP2_DSS_COLLECT_IRQ_STATS`, `FB_OMAP2_DSS_DPI`, `FB_OMAP2_DSS_VENC`, `FB_OMAP2_DSS_HDMI_COMMON`, `FB_OMAP4_DSS_HDMI`, `FB_OMAP5_DSS_HDMI`, `FB_OMAP2_DSS_SDI`, `FB_OMAP2_DSS_DSI`, `FB_OMAP2_DSS_MIN_FCK_PER_PCK`, and `FB_OMAP2_DSS_SLEEP_AFTER_VENC_RESET`.

## Control Flow

This is build-time control flow. Enabling `FB_OMAP2_DSS` selects `VIDEOMODE_HELPERS`, `FB_OMAP2_DSS_INIT`, and `HDMI`; sub-options determine which objects the Makefile adds and which code paths are compiled. Debugfs and IRQ statistics are nested so IRQ stats are available only when debugfs support is enabled.

## State and Persistence Behavior

Kconfig values persist in the kernel `.config` and drive compile-time feature selection. Runtime behavior is affected by these symbols but the file itself owns no runtime state.

## Dependencies and Integration Points

The file feeds `dss/Makefile` object selection and `#ifdef CONFIG_FB_OMAP2_DSS_*` branches across DSS sources. `FB_OMAP2_DSS_MIN_FCK_PER_PCK` is used by DISPC divisor selection to constrain functional clock to pixel clock ratio.

## Risks and Edge Cases

Defaults enable DPI, VENC, and OMAP4 HDMI when the parent is enabled, which can expand build surface. `FB_OMAP2_DSS` is a tristate but many child outputs are bools, so module/built-in combinations need build coverage. The integer clock ratio can make otherwise valid display timings fail if set too high.

## Test Signals

Signals include allmodconfig/allyesconfig builds, minimal DSS builds, debugfs and IRQ-stat build variants, HDMI4/HDMI5 separate builds, and runtime validation that selected output drivers are registered or omitted as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Makefile

## Purpose

`dss/Makefile` maps the OMAP DSS Kconfig symbols to built objects. The complete 18-line file was read. It builds the boot init object, the main `omapdss.o` composite module/object, core DSS files, compatibility-layer files, and optional output-specific files.

## Important APIs, Types, and Functions

The important build variables are `obj-$(CONFIG_FB_OMAP2_DSS_INIT)`, `obj-$(CONFIG_FB_OMAP2_DSS)`, `omapdss-y`, and option-specific `omapdss-$(CONFIG_...)` additions. Core entries include `core.o`, `dss.o`, `dss_features.o`, `dispc.o`, `dispc_coefs.o`, `display.o`, `output.o`, `dss-of.o`, `pll.o`, and `video-pll.o`. Compatibility entries include `manager.o`, `manager-sysfs.o`, `overlay.o`, `overlay-sysfs.o`, `apply.o`, `dispc-compat.o`, and `display-sysfs.o`.

## Control Flow

This file controls link composition rather than runtime execution. The order places core DSS and DISPC support before compatibility wrappers and then optional interface drivers. `ccflags-$(CONFIG_FB_OMAP2_DSS_DEBUG) += -DDEBUG` controls debug logging compilation.

## State and Persistence Behavior

There is no runtime state. Build outputs persist in the kernel build tree according to configuration.

## Dependencies and Integration Points

It consumes symbols from `dss/Kconfig` and integrates the core DSS component, overlay/manager compatibility APIs, and output drivers into one `omapdss` unit. Conditional HDMI common and HDMI4/HDMI5 object groups mirror the Kconfig split.

## Risks and Edge Cases

Because many files cross-call initialization functions, removing or reordering objects can expose unresolved symbols. Optional output drivers must match the init/uninit arrays in `core.c`. Debug flag behavior changes logging volume and may expose timing-sensitive messages.

## Test Signals

Signals include configured builds for each output subset, module and built-in builds of `FB_OMAP2_DSS`, compile checks with `FB_OMAP2_DSS_DEBUG`, and symbol/link validation for HDMI_COMMON without the wrong HDMI generation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/apply.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/apply.c

## Purpose

`apply.c` is the legacy OMAP DSS compatibility apply layer that bridges fbdev overlay/manager APIs to DISPC hardware programming. The complete 1690-line file was read. It manages cached overlay/manager state, validates configurations, writes DISPC registers, schedules GO bits, handles VSYNC/FRAMEDONE completion, and installs compatibility manager/overlay operations.

## Important APIs, Types, and Functions

`struct ovl_priv_data` holds user overlay info, active info, dirty/shadow flags, enabled/enabling state, and FIFO thresholds. `struct mgr_priv_data` holds manager info, busy/updating/enabled flags, timing/LCD config, and framedone callback. Global `dss_data` is protected by `data_lock`; blocking sequences use `apply_lock`; extra-info waits use `extra_updated_completion`. Key functions include `dss_check_settings_low()`, `need_isr()`, `dss_mgr_wait_for_vsync()`, `dss_mgr_wait_for_go()`, `dss_ovl_write_regs()`, `dss_mgr_write_regs()`, `dss_set_go_bits()`, `dss_apply_irq_handler()`, `omap_dss_mgr_apply()`, manager/overlay enable/disable/set-info/set-manager helpers, and exported `omapdss_compat_init()` / `omapdss_compat_uninit()`.

## Control Flow

The layer maintains four configuration levels: user cache from `set_info()`, apply cache after `apply()`, DISPC shadow registers after register writes, and live registers after VFP or output enable. User calls set overlay/manager info under spinlock, then `apply()` validates current plus dirty state, copies user info into active info, writes registers when the manager can accept them, and sets GO bits. For automatic update managers, VSYNC IRQs clear busy/shadow state and advance pending writes. For manual update managers, `start_update` writes registers, enables output, and waits for FRAMEDONE to invoke callbacks.

## State and Persistence Behavior

State is entirely in kernel memory and DISPC shadow/live registers. Dirty flags model pending updates across IRQ boundaries. Manager `busy` tracks GO bit ownership; `updating` tracks enabled DISPC output; `extra_info_dirty` is used for enable, FIFO threshold, timing, and LCD-config changes that must be written even for disabled overlays. `compat_refcnt` allows nested compatibility init/uninit.

## Dependencies and Integration Points

The file depends on overlay/manager lists from DSS core, `dss_mgr_check()` / simple checks from manager/overlay code, DISPC programming APIs, `dispc-compat` IRQ helpers, display sysfs initialization, overlay/manager sysfs initialization, and runtime PM via `dispc_runtime_get()`. It installs `dss_mgr_ops` and populates function pointers in every `omap_overlay_manager` and `omap_overlay`.

## Risks and Edge Cases

Most correctness depends on lock ordering between `apply_lock`, `data_lock`, and DISPC IRQ callbacks. GO waits use fixed 500 ms timeouts and tolerate the fourth-iteration failure by returning 0 after logging. Manual update overlays may need a dummy update before manager detachment; current code returns `-EINVAL`. Register writes can be skipped if validation fails, leaving dirty state pending. Error paths in init must balance display sysfs, manager ops, overlay sysfs, IRQ setup, and runtime PM.

## Test Signals

Signals include overlay enable/disable, manager enable/disable, changing overlay info while active, GO wait behavior on automatic outputs, manual update FRAMEDONE callbacks, FIFO threshold recalculation, invalid configuration rejection, changing managers while overlays are disabled/enabled, suspend/resume display state, and repeated `omapdss_compat_init()` / `uninit()` refcount coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/apply.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/core.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/core.c

## Purpose

`core.c` is the top-level OMAP DSS platform driver and module init/exit coordinator. The complete 287-line source was read. It stores the core platform device, exposes board-level helpers, initializes feature tables and debugfs, registers PM notifications, and registers/unregisters all DSS output platform drivers.

## Important APIs, Types, and Functions

Global `core` stores `pdev` and `default_display_name`; `def_disp` is a module parameter. Exported helpers include `omapdss_get_default_display_name()`, `omapdss_get_version()`, `dss_get_core_pdev()`, `dss_dsi_enable_pads()`, `dss_dsi_disable_pads()`, and `dss_set_min_bus_tput()`. Debugfs helpers include `dss_debugfs_create_file()` when enabled. Platform lifecycle is handled by `omap_dss_probe()`, `remove()`, `shutdown()`, `omap_dss_init()`, and `omap_dss_exit()`.

## Control Flow

Module init probes the `omapdss` platform driver, initializes DSS features from board data, creates debugfs, stores default display override, registers a PM notifier, then iterates `dss_output_drv_reg_funcs` to register DSS, DISPC, and configured output drivers. On registration failure it unwinds with the reverse unregistration table. PM notifications suspend active displays before suspend/hibernate/restore and resume them afterward. Shutdown disables all active displays.

## State and Persistence Behavior

Persistent runtime state is limited to the static `core` struct and registered driver/module state. Default display name persists for the module lifetime. Display suspend intent is held per `omap_dss_device` in display code, not here.

## Dependencies and Integration Points

The file depends on platform data `struct omap_dss_board_info`, DSS feature initialization, display suspend/resume helpers, debugfs, and each output driver's init/uninit function. It is the source for `dss_get_core_pdev()`, used by compatibility init for sysfs parentage.

## Risks and Edge Cases

The code assumes platform data is valid when `omapdss_get_version()` is called. The init error unwind index expression is subtle and depends on registration array ordering matching unregistration order. PM notifier callbacks call into display drivers and can fail only by returning the display helper's status, which is currently always 0.

## Test Signals

Signals include module init/uninit with every Kconfig output combination, failure injection in output driver registration, PM notifier suspend/resume path with active displays, shutdown disabling displays, debugfs creation/removal, and `def_disp` module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.c

## Purpose

`dispc-compat.c` is the legacy DISPC interrupt compatibility layer. The complete 658-line source was read. It multiplexes DISPC IRQs to registered legacy callbacks, tracks optional IRQ statistics, masks and recovers from unhandled DISPC error interrupts, and provides synchronous manager enable/disable and wait-for-IRQ helpers.

## Important APIs, Types, and Functions

`struct omap_dispc_isr_data` stores callback, argument, and mask; `struct dispc_irq_stats` stores debug counters. Global `dispc_compat` holds the IRQ lock, error mask, up to `DISPC_MAX_NR_ISRS` registered clients, pending error bits, error work, and optional stats. Exported functions include `omap_dispc_register_isr()`, `omap_dispc_unregister_isr()`, `dss_dispc_initialize_irq()`, `dss_dispc_uninitialize_irq()`, `dispc_mgr_enable_sync()`, `dispc_mgr_disable_sync()`, and `omap_dispc_wait_for_irq_interruptible_timeout()`.

## Control Flow

Initialization sets lock/stat state, builds the default error mask based on DSS features, clears stale IRQ status, initializes error work, writes IRQ enable bits, and registers a DISPC IRQ handler through `dispc_request_irq()`. The IRQ handler reads status/enable, ignores unrelated IRQs, optionally records stats, acks status, copies registered callbacks, dispatches matching callbacks outside the lock, then masks unhandled error bits and schedules `dispc_error_worker()`. The worker disables underflowing overlays, restarts managers on sync-lost with video overlays disabled, disables all managers on OCP errors, then restores the error mask.

## State and Persistence Behavior

State is volatile global kernel state. Registered ISR slots persist until unregistered. Error bits are held until the workqueue processes them. Optional stats persist until debugfs read resets them. Hardware IRQ enable state is recomputed from error mask plus client masks.

## Dependencies and Integration Points

The file depends on DISPC MMIO wrappers in `dispc.c`, runtime PM, DSS feature flags, overlay/manager lookup and enable/disable operations, debugfs registration from `core.c`, and completion/wait primitives. `apply.c` relies on the ISR registration and wait helpers for VSYNC, GO, and FRAMEDONE synchronization.

## Risks and Edge Cases

Only eight ISR clients can register, and duplicate entries are rejected by exact callback/arg/mask match. Error recovery calls high-level overlay/manager operations from a workqueue after IRQ context, which can interact with apply locks. Digit output disable falls back to VSYNC counting on older hardware without TV framedone IRQ and is explicitly not fully reliable. IRQ masks are recomputed under lock, but callbacks can unregister themselves only because the handler dispatches from a copied array.

## Test Signals

Signals include registering/unregistering duplicate and maximum ISR slots, waiting for IRQ with timeout and signal interruption, injected FIFO underflow/sync-lost/OCP error bits, debugfs IRQ statistics reset on read, LCD and DIGIT synchronous enable/disable paths, and cleanup freeing the DISPC IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.h

## Purpose

`dispc-compat.h` is the small internal header for DISPC compatibility helpers. The complete 19-line file was read. It declares synchronous manager enable/disable, wait-for-IRQ, and IRQ init/uninit functions implemented by `dispc-compat.c`.

## Important APIs, Types, and Functions

Declared APIs are `dispc_mgr_enable_sync()`, `dispc_mgr_disable_sync()`, `omap_dispc_wait_for_irq_interruptible_timeout()`, `dss_dispc_initialize_irq()`, and `dss_dispc_uninitialize_irq()`.

## Control Flow

The header has no runtime control flow. It allows `apply.c` and related DSS code to call the IRQ compatibility layer without exposing implementation details.

## State and Persistence Behavior

No state is defined here; state lives in `dispc-compat.c` and DISPC hardware registers.

## Dependencies and Integration Points

The declarations rely on OMAP DSS enum and integer types available through the surrounding DSS include graph. It is included by `apply.c` and `dispc-compat.c`.

## Risks and Edge Cases

The header does not include a type header itself, so include order must provide `enum omap_channel`, `u32`, and `unsigned long`. Any signature change must be kept in sync with `dispc-compat.c` and callers.

## Test Signals

Signals are compile-only: include-order builds, warnings as errors, and successful linking of `apply.o` with `dispc-compat.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.c

## Purpose

`dispc.c` is the hardware-facing OMAP Display Controller driver for the legacy fbdev DSS stack. The complete 4059-line source was read. It owns DISPC MMIO access, context save/restore, runtime PM, overlay setup, scaler calculations, FIFO/MFLAG setup, manager timing and clock programming, IRQ request plumbing, debug register dumps, and platform/component binding.

## Important APIs, Types, and Functions

Key types are `struct dispc_features`, the static `dispc` device state, `enum mgr_reg_fields`, `struct dispc_reg_field`, and color/scaler helper types. Exported or externally used APIs include `dispc_runtime_get()/put()`, manager IRQ accessors, `dispc_mgr_go_busy()`, `dispc_mgr_go()`, `dispc_ovl_set_channel_out()`, `dispc_ovl_set_fifo_threshold()`, `dispc_ovl_compute_fifo_thresholds()`, `dispc_ovl_check()`, `dispc_ovl_setup()`, `dispc_ovl_enable()`, `dispc_ovl_enabled()`, `dispc_mgr_enable()`, `dispc_mgr_is_enabled()`, `dispc_mgr_setup()`, `dispc_mgr_set_lcd_config()`, `dispc_mgr_timings_ok()`, `dispc_mgr_set_timings()`, clock/divider helpers, IRQ status/enable helpers, and platform driver init/uninit.

## Control Flow

Probe registers a component. Bind selects SoC features from `omapdss_get_version()`, maps MMIO, gets IRQ, optionally finds a `syscon-pol` regmap, enables runtime PM, performs initial hardware configuration, reads revision, initializes overlay managers, and creates debugfs. Overlay setup validates color mode, addresses, YUV alignment, interlace field mode, scaling limits, predecimation, and clock requirements; then it calculates DMA/VRFB/TILER offsets, row/pixel increments, FIR coefficients, chroma handling, color conversion, z-order, alpha, replication, and base addresses. Manager setup programs default color, transparency key, alpha/z-order, CPR, LCD timing, data lines, stall mode, and clock divisors.

## State and Persistence Behavior

The static `dispc` struct stores MMIO base, IRQ, user IRQ handler, clock rates, FIFO sizes/assignments, saved register context, SoC feature table, enabled flag, syscon polarity regmap, and a control/config spinlock. Runtime suspend marks DISPC disabled, synchronizes IRQ, and saves register context; resume reinitializes hardware if load mode indicates context loss and restores saved context before re-enabling IRQ handling. Hardware register state is authoritative only while powered.

## Dependencies and Integration Points

The file integrates with DSS clock/PLL helpers, feature tables, overlay manager initialization, `dispc_coefs.c` for scaler coefficient tables, runtime PM, component framework, DT compatibles, debugfs from `core.c`, regmap/syscon polarity bits, and `dispc-compat.c` through IRQ request and MMIO IRQ helpers. `apply.c` uses most overlay/manager programming exports.

## Risks and Edge Cases

Many helper paths use `BUG()` for impossible enum values, so invalid callers can panic the kernel. Scaling calculations are SoC-specific and depend on current clock rates; wrong divisors or `CONFIG_FB_OMAP2_DSS_MIN_FCK_PER_PCK` can reject valid-looking modes. Rotation offset math is format-specific and has special NV12 and interlace behavior. Context save/restore intentionally delays CONTROL and IRQENABLE restore until late. FIFO/MFLAG setup includes documented hardware workarounds. IRQ handler dispatch uses memory barriers around `is_enabled` and user handler state.

## Test Signals

Signals include SoC feature selection across OMAP24xx/34xx/44xx/54xx/DRA7, runtime suspend/resume with context loss, overlay setup for RGB/YUV/NV12, scaling up/down including 3-tap/5-tap, interlace and rotation modes, FIFO threshold calculations, manager timing bounds, clock divisor search, debugfs register dumps, IRQ request/free, and DT `syscon-pol` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.h

## Purpose

`dispc.h` is the DISPC register map and inline register-address helper header. The complete 907-line file was read. It defines common, manager, overlay, FIR, writeback, preload, and MFLAG register offsets plus helper functions mapping `enum omap_channel` and `enum omap_plane` to SoC register addresses used by `dispc.c`.

## Important APIs, Types, and Functions

The public data type is `struct dispc_coef`, used by `dispc_coefs.c` and scaler programming. It declares `dispc_ovl_get_scale_coef()`. Macros include `DISPC_REVISION`, `DISPC_IRQSTATUS`, `DISPC_CONTROL`, `DISPC_CONFIG`, `DISPC_OVL_*`, and `DISPC_*` register constructors. Inline helpers include manager helpers such as `DISPC_DEFAULT_COLOR()`, `DISPC_TIMING_H()`, `DISPC_DIVISORo()`, and overlay helpers such as `DISPC_OVL_BASE()`, `DISPC_BA0_OFFSET()`, `DISPC_FIR_COEF_*_OFFSET()`, `DISPC_PRELOAD_OFFSET()`, and `DISPC_MFLAG_THRESHOLD_OFFSET()`.

## Control Flow

The header has no independent runtime flow, but its inline switches execute whenever `dispc.c` computes MMIO addresses. Unsupported channel/plane combinations intentionally call `BUG()` and return 0.

## State and Persistence Behavior

No runtime state is owned by the header. It defines compile-time register constants and offset calculations for DISPC hardware state.

## Dependencies and Integration Points

It depends on OMAP DSS enum definitions from the include graph. `dispc.c` uses it for every register access, and `dispc_coefs.c` uses `struct dispc_coef` plus the coefficient lookup declaration.

## Risks and Edge Cases

The offset helpers encode hardware layout assumptions for different overlays, managers, and writeback. Several helpers deliberately reject GFX or DIGIT combinations. Any register offset error can silently program the wrong hardware register. The header mixes base macros and inline offsets, so callers must choose the right constructor for plane/manager type.

## Test Signals

Signals include compile coverage for all helpers, register dump comparison against TRM offsets, exercising GFX/video/writeback code paths, OMAP4+ LCD2/LCD3 coverage, and avoiding unsupported enum combinations in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc_coefs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc_coefs.c

## Purpose

`dispc_coefs.c` supplies the hard-coded DISPC FIR scaler coefficient tables used by overlay scaling. The complete 314-line source was read. It defines 3-tap and 5-tap coefficient arrays for multiple M ranges and exposes a lookup helper.

## Important APIs, Types, and Functions

The file defines `static const struct dispc_coef` arrays `coef3_M8` through `coef3_M32` and `coef5_M8` through `coef5_M32`, each with eight phases. The only function is `dispc_ovl_get_scale_coef(int inc, int five_taps)`, which maps a FIR increment bucket to either the 3-tap or 5-tap table.

## Control Flow

Lookup divides `inc` by 128, walks a descending table of `{Mmin, Mmax, coef_3, coef_5}`, and returns the matching table pointer. Upscaling stronger than 2x intentionally maps to M11, M16, or M19 tables instead of M8 to reduce visible blockiness and outlines. If no bucket matches, it returns `NULL`.

## State and Persistence Behavior

All coefficient data is static read-only kernel data. There is no mutable state or persistence outside the compiled image.

## Dependencies and Integration Points

The file depends on `struct dispc_coef` from `dispc.h` and is consumed by `dispc_ovl_set_scale_coef()` in `dispc.c` when programming horizontal, vertical, and chroma FIR registers.

## Risks and Edge Cases

Returned `NULL` is not checked by `dispc_ovl_set_scale_coef()`, so scaling calculations must keep `inc` in supported ranges. Coefficients are hardware- and quality-sensitive; accidental edits can introduce image artifacts. The table uses signed 8-bit fields, so values must stay within the expected hardware format.

## Test Signals

Signals include lookup tests for every M bucket boundary, upscaling buckets 0-3, both 3-tap and 5-tap paths, display scaling visual tests, and static checks that callers do not request out-of-range increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc_coefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display-sysfs.c

## Purpose

`display-sysfs.c` creates legacy per-display sysfs attributes for OMAP DSS devices. The complete 347-line source was read. It exposes display identity, enabled state, TE, timings, rotation, mirror, and WSS controls by routing sysfs operations to `omap_dss_driver` callbacks.

## Important APIs, Types, and Functions

Show/store helpers include `display_name_show()`, `display_enabled_show/store()`, `display_tear_show/store()`, `display_timings_show/store()`, `display_rotate_show/store()`, `display_mirror_show/store()`, and `display_wss_show/store()`. `struct display_attribute` wraps a sysfs attribute with DSS show/store callbacks. `display_init_sysfs()` creates a kobject per registered display, and `display_uninit_sysfs()` removes them.

## Control Flow

Compatibility init calls `display_init_sysfs()`, which iterates all displays with `for_each_dss_dev()` and creates kobjects under the DSS platform device kobject using display aliases. Sysfs read/write dispatch uses `container_of()` to recover the DSS device and selected display attribute. Enabling writes call driver `enable()` or `disable()` after parsing booleans. Timing writes parse PAL/NTSC aliases when VENC is enabled or numeric timing strings, check timings, disable the display, set timings, then re-enable it.

## State and Persistence Behavior

The sysfs layer owns only the kobject lifecycle. Actual display state remains in each `omap_dss_device` and panel/output driver. Timings, rotate, mirror, and WSS writes persist only in those driver states or hardware until changed/unbound.

## Dependencies and Integration Points

It depends on display registration from `display.c`, driver callback completeness, sysfs/kobject APIs, `kstrtox`, and optional VENC timing constants. It is initialized and removed by `omapdss_compat_init()` / `uninit()` in `apply.c`.

## Risks and Edge Cases

The timing store path disables before setting timings and attempts to re-enable; if enable fails, the display remains off. Attribute availability is dynamic: unsupported callbacks return `-ENOENT`. There is no central display mutex here, so serialization relies on lower drivers. Kobject cleanup zeroes the embedded kobject after put, which assumes no outstanding sysfs references beyond normal kobject lifetime rules.

## Test Signals

Signals include sysfs read/write for every attribute, unsupported callback paths returning `-ENOENT`, invalid timing parsing, timing change failure recovery, enable writes on disconnected displays, PAL/NTSC parsing under VENC builds, and init/uninit with multiple registered displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display.c

## Purpose

`display.c` implements OMAP DSS display registration, enumeration, refcounting, suspend/resume helpers, default display callbacks, and conversions between generic `videomode` and `omap_video_timings`. The complete 328-line source was read.

## Important APIs, Types, and Functions

Default callbacks are `omapdss_default_get_resolution()`, `omapdss_default_get_recommended_bpp()`, and `omapdss_default_get_timings()`. System-wide helpers are `dss_suspend_all_devices()`, `dss_resume_all_devices()`, and `dss_disable_all_devices()`. Registration/refcount APIs are `omapdss_register_display()`, `omapdss_unregister_display()`, `omap_dss_get_device()`, `omap_dss_put_device()`, `omap_dss_get_next_device()`, and `omap_dss_find_device()`. Timing conversion APIs are `videomode_to_omap_video_timings()` and `omap_video_timings_to_videomode()`.

## Control Flow

Panel drivers call `omapdss_register_display()` after filling an `omap_dss_device`; the function assigns a `displayN` alias using DT alias ID or a counter, reads an optional DT `label`, fills missing default callbacks, and appends the device to `panel_list` under `panel_list_mutex`. Enumeration gets a module/device reference for returned devices and drops the previous reference. Suspend disables active displays and marks them for resume; resume enables only devices marked `activate_after_resume`.

## State and Persistence Behavior

Global state is the display list, list mutex, and alias counter. Per-display state includes alias/name, callback pointers, panel timings, `state`, and `activate_after_resume`. There is no file-backed persistence; names and aliases live for the bound device lifetime.

## Dependencies and Integration Points

The file integrates with panel/output drivers, OF aliases and labels, module/device refcounting, DSS PM notifier in `core.c`, sysfs iteration in `display-sysfs.c`, and generic videomode helpers selected by Kconfig.

## Risks and Edge Cases

`omap_dss_get_next_device()` drops the previous device reference while holding the list mutex and warns if the previous device is no longer in the list. Mixed DT/non-DT assumptions are documented and can affect alias numbering. Default recommended BPP uses display type heuristics and may not match every panel. Suspend/resume ignores enable errors because helpers return 0.

## Test Signals

Signals include registration/unregistration ordering, DT alias/label naming, enumeration refcount correctness, suspend/resume of active and inactive displays, default BPP for all display types, timing conversion round trips, and concurrent display iteration during removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display.c -->
