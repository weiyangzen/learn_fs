# Research: subset-b-003704

Grouped source research for subset B work item `subset-b-003704`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm69299.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm69299.c

## Purpose
This file is a DRM MIPI-DSI panel driver for Visionox RM69299-based AMOLED panels. It supports two compatible variants with different fixed modes, initialization command tables, and optional backlight limits.

## Important APIs, Types, and Functions
The main state is `struct visionox_rm69299`, backed by `struct visionox_rm69299_panel_desc` for variant mode/init data. Key functions are `visionox_rm69299_power_on`, `visionox_rm69299_power_off`, `visionox_rm69299_prepare`, `visionox_rm69299_unprepare`, `visionox_rm69299_get_modes`, brightness get/update callbacks, `visionox_rm69299_probe`, and `visionox_rm69299_remove`.

## Control Flow
Probe allocates a `drm_panel`, reads OF match data, gets `vdda` and `vdd3p3` regulators plus a reset GPIO, optionally registers a raw backlight, adds the panel, configures four-lane RGB888 DSI video mode, and attaches to the host. Prepare enables regulators, runs the reset timing, switches to low-power DSI mode, writes the selected init table as two-byte DCS packets, exits sleep, waits, and turns the display on. Unprepare disables low-power mode, sends display-off and sleep commands, then powers down.

## State and Persistence Behavior
Persistent driver state is devm-managed: panel object, regulator array, reset GPIO, DSI pointer, selected descriptor, and optional backlight. Runtime state is mostly external hardware state: regulator enables, reset line level, DSI mode flags, panel sleep/display state, and DCS brightness.

## Dependencies and Integration Points
It integrates with DRM panel helpers, MIPI DSI multi-command helpers, device-tree match data, regulator and GPIO frameworks, and the Linux backlight class. The mode is exposed through connector probing and the module binds through `module_mipi_dsi_driver`.

## Risks
The init tables are opaque vendor sequences, so mode or timing changes can silently break bring-up. Brightness callbacks temporarily clear `MIPI_DSI_MODE_LPM`; failures before restoring the flag can leave later transfers in the wrong mode. Power-on and DCS delays are panel-specific and sensitive to shortening. The 1080p descriptor has no backlight bounds, so no backlight is created for that variant.

## Test Signals
Useful signals are DSI attach/probe on both compatibles, panel prepare/unprepare cycles, suspend/resume, display mode enumeration, brightness read/write through sysfs, regulator/reset scope traces, and display-on/off timing checks against the DCS 120 ms waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm69299.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm692e5.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm692e5.c

## Purpose
This file implements a DRM MIPI-DSI command-mode panel driver for the Visionox RM692E5. It programs a long vendor initialization sequence, exposes 1080x2400 modes at 120/90/60 Hz, and configures DSC compression.

## Important APIs, Types, and Functions
The main state is `struct visionox_rm692e5`, containing `drm_panel`, `mipi_dsi_device`, `drm_dsc_config`, reset GPIO, and bulk regulators. Important functions are `visionox_rm692e5_reset`, `visionox_rm692e5_on`, `visionox_rm692e5_prepare`, `visionox_rm692e5_disable`, `visionox_rm692e5_unprepare`, `visionox_rm692e5_get_modes`, large-brightness callbacks, and probe/remove.

## Control Flow
Probe allocates the panel, acquires `vddio` and `vdd`, gets an active-high reset GPIO, sets four DSI lanes and RGB888 format, registers a 12-bit raw backlight, fills DSC version/slice/bpp fields, and attaches with devm DSI. Prepare enables regulators, toggles reset, sends the vendor on-sequence in low-power mode, packs and sends the DSC PPS, enables DSI compression mode, waits, and returns accumulated transfer status. Disable sends display-off and sleep commands; unprepare asserts reset and disables supplies.

## State and Persistence Behavior
State persists in the panel object, DSI pointer, DSC config, supplies, reset line, and backlight device. Hardware state includes programmed DCS pages, DSC PPS, compression enable, sleep/display state, and 12-bit brightness. No persistent software cache of brightness is kept beyond the backlight core.

## Dependencies and Integration Points
The driver depends on DRM panel/probe helpers, DRM DSC PPS packing, MIPI DSI compression helpers, regulator/GPIO frameworks, and the backlight subsystem. It binds to `visionox,rm692e5` through OF and exports a `mipi_dsi_driver`.

## Risks
DSC parameters must match both panel firmware and host encoder setup; wrong slice width or bpp will produce link corruption. The generated vendor sequence is hard to audit. Brightness operations clear LPM and return early on error without restoring it. Error handling in prepare disables regulators but does not send a DCS off sequence after partial initialization.

## Test Signals
Signals include successful mode enumeration for all three refresh rates, DSC PPS matching host logs, prepare/disable/unprepare cycles, brightness range tests from 0 to 4095, DSI transfer error injection, and visual validation at 60/90/120 Hz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-rm692e5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-vtdr6130.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-vtdr6130.c

## Purpose
This is a DRM panel driver for the Visionox VTDR6130 AMOLED DSI panel. It provides a fixed 1080x2400 144 Hz mode, vendor DCS initialization, regulator/reset sequencing, and raw backlight control.

## Important APIs, Types, and Functions
`struct visionox_vtdr6130` stores the DRM panel, DSI device, reset GPIO, and three supplies. Core functions are `visionox_vtdr6130_reset`, `visionox_vtdr6130_on`, `visionox_vtdr6130_off`, prepare/unprepare, mode enumeration, `visionox_vtdr6130_bl_update_status`, and DSI probe/remove.

## Control Flow
Probe allocates the panel, gets `vddio`, `vci`, and `vdd`, obtains reset, sets four-lane RGB888 DSI video mode with no EOT and non-continuous clock, registers a 4095-step raw backlight, adds the panel, and attaches. Prepare enables all supplies, runs reset, sends tear-on, display control, brightness, page/keyed vendor tables, exits sleep, waits 120 ms, and turns the panel on. Unprepare sends display-off and sleep, asserts reset, and disables regulators.

## State and Persistence Behavior
The file keeps only device lifetime state. Hardware state persists across prepare until unprepare: regulator rails, reset state, DSI mode flags, panel command pages, sleep/display state, and current DCS brightness value.

## Dependencies and Integration Points
It uses DRM panel and MIPI DSI helpers, Linux regulator and GPIO consumers, OF matching for `visionox,vtdr6130`, and the backlight core. Connector physical size is populated from the fixed mode.

## Risks
The on-sequence contains many undocumented command pages and magic values. The backlight update callback does not force low-power mode like the prepare path, so host requirements for DCS brightness transfers matter. Failure during `visionox_vtdr6130_off` is not propagated. Timing is tuned for the panel and may not tolerate aggressive PM.

## Test Signals
Important tests include probe/attach, repeated prepare/unprepare, mode probe at 144 Hz, brightness writes across the 0-4095 range, suspend/resume with regulator sequencing, and oscilloscope or host logs for reset and DSI command timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-vtdr6130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-widechips-ws2401.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-widechips-ws2401.c

## Purpose
This file drives a WideChips WS2401-controlled Samsung LMS380KF01 480x800 DPI RGB panel over SPI/MIPI DBI. It handles panel power, DBI initialization, optional internal backlight, and DRM panel mode exposure.

## Important APIs, Types, and Functions
The state container is `struct ws2401`, embedding `mipi_dbi`, `drm_panel`, reset GPIO, two regulators, dimensions, and an `internal_bl` flag. Main functions are `ws2401_power_on`, `ws2401_power_off`, panel prepare/enable/disable/unprepare, `ws2401_get_modes`, `ws2401_set_brightness`, `ws2401_read_mtp_id`, probe, and remove.

## Control Flow
Probe allocates a DPI panel, gets `vci` and `vccio`, configures reset, initializes DBI over SPI, assigns readable ID commands, briefly powers the panel to read MTP ID, powers it off, then uses an external DT backlight if present or registers an internal platform backlight. Prepare enables rails, toggles reset, sends repeated sleep-out plus password, resolution, address mode, pixel format, SMPS, power, VCOM, source, panel, MIE, and gamma commands. Enable sends display-on; disable sends display-off; unprepare disables the internal backlight if used, enters sleep, and powers off.

## State and Persistence Behavior
The driver persists SPI DBI bus state, panel registration, reset/regulator handles, and optional backlight selection. The panel itself retains register programming while powered. Internal backlight brightness is controlled by DCS-like DBI commands and not mirrored in private state.

## Dependencies and Integration Points
It integrates with DRM panel, `drm_mipi_dbi`, SPI, regulator/GPIO, media bus format reporting, external `drm_panel_of_backlight`, and Linux backlight. It exposes RGB888 bus format and pixel-drive bus flags to the display pipeline.

## Risks
The driver ignores return values from most DBI commands during power-on, so partial initialization may look successful. Internal backlight requires leaving level-2 command access open; external backlight closes it. Probe intentionally powers the panel for ID reads, which can interact with board sequencing. The implementation is tailored to LMS380KF01 despite a reusable controller name.

## Test Signals
Validate SPI DBI transfers, MTP ID reads, power cycling, display-on/off, RGB bus timing and flags, external versus internal backlight paths, gamma/register initialization on real hardware, and blanking behavior through backlight sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-widechips-ws2401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-xinpeng-xpp055c272.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-xinpeng-xpp055c272.c

## Purpose
This file implements a DRM MIPI-DSI panel driver for the Xinpeng XPP055C272 5.5-inch 720x1280 panel. It provides fixed timing, regulator/reset sequencing, a vendor initialization sequence, and optional DT-provided backlight integration.

## Important APIs, Types, and Functions
The main state is `struct xpp055c272`, holding device, panel, reset GPIO, `vci`, and `iovcc`. Key functions are `xpp055c272_init_sequence`, `xpp055c272_prepare`, `xpp055c272_unprepare`, `xpp055c272_get_modes`, `xpp055c272_probe`, and `xpp055c272_remove`.

## Control Flow
Probe allocates a DSI panel, gets optional reset and required regulators, configures four-lane RGB888 burst video mode with low-power and no-EOT flags, resolves a DT backlight, adds the panel, and attaches to DSI. Prepare enables `vci` then `iovcc`, toggles reset with vendor timing, sends the vendor command sequence through `mipi_dsi_multi_context`, exits sleep, waits 120 ms, turns display on, and waits 50 ms. Unprepare sends display-off and sleep, then disables `iovcc` and `vci`.

## State and Persistence Behavior
Private software state is limited to devm-managed resources. Hardware state is the active regulator state, reset line, panel command registers, sleep/display state, and external backlight state if the panel has one.

## Dependencies and Integration Points
It depends on DRM panel, MIPI DSI multi-command helpers, regulator/GPIO consumers, OF matching for `xinpeng,xpp055c272`, media bus/display timing definitions, and optional `drm_panel_of_backlight`.

## Risks
The initialization sequence is vendor-supplied and undocumented. If `reset_gpio` is absent, prepare still calls `gpiod_set_value_cansleep` safely but board-level reset assumptions change. Unprepare returns DCS errors before disabling regulators, so a command failure can leave rails enabled. The fixed mode and DSI burst flags must match the host and panel timing budget.

## Test Signals
Signals include DSI attach, fixed mode enumeration, regulator enable/disable order, reset timing, init-sequence transfer errors, display sleep/display-on cycles, external backlight integration, and visual validation at 720x1280.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-xinpeng-xpp055c272.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Kconfig

## Purpose
This Kconfig entry exposes the Panfrost DRM driver for ARM Mali Midgard and Bifrost GPUs.

## Important APIs, Types, and Functions
It defines `config DRM_PANFROST` as a tristate. It selects DRM scheduler, IOMMU LPAE page-table support, GEM shmem helpers, PM devfreq with simple_ondemand governor, and device coredump support.

## Control Flow
There is no runtime control flow. Build selection is gated on DRM, ARM/ARM64 or compile-test, absence of `GENERIC_ATOMIC64`, and MMU support.

## State and Persistence Behavior
The file stores build-time dependency state only. Enabling it causes the Panfrost module or built-in object to compile and makes dependent subsystems available.

## Dependencies and Integration Points
The entry integrates Panfrost with the DRM core, IOMMU io-pgtable LPAE backend, DRM GPU scheduler, shmem GEM helpers, devfreq, thermal/devfreq governor infrastructure, and devcoredump.

## Risks
The `!GENERIC_ATOMIC64` dependency is tied to LPAE page-table implementation constraints and can surprise compile-test coverage. Missing selected subsystems would break core driver features such as MMU mapping, scheduling, GEM allocation, and crash dumps.

## Test Signals
Build tests should cover built-in and module configurations on ARM, ARM64, and COMPILE_TEST platforms, including dependency resolution for `DRM_SCHED`, `IOMMU_IO_PGTABLE_LPAE`, `PM_DEVFREQ`, and `WANT_DEV_COREDUMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Makefile

## Purpose
This Makefile defines the object composition for the Panfrost DRM driver.

## Important APIs, Types, and Functions
It builds `panfrost.o` from driver, device, devfreq, GEM, shrinker, GPU, job manager, MMU, performance counter, and dump objects. `obj-$(CONFIG_DRM_PANFROST)` links the aggregate when the Kconfig option is enabled.

## Control Flow
There is no runtime control flow. The link order places the platform/DRM driver and subsystem implementations into one module or built-in object.

## State and Persistence Behavior
The file controls build artifacts only. Any source omitted here is not part of the final Panfrost driver, and any added object becomes part of the module ABI surface indirectly through internal symbols.

## Dependencies and Integration Points
It integrates the Panfrost submodules with Kbuild and the `CONFIG_DRM_PANFROST` selection path from Kconfig.

## Risks
Forgetting to list a new implementation file causes unresolved references or missing functionality. Removing an object can disable required initialization stages such as MMU, scheduler, shrinker, perfcnt, or devcoredump.

## Test Signals
Signals are clean module and built-in builds, modpost without unresolved symbols, and runtime probe confirming all subsystem init functions linked from this object list are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.c

## Purpose
This file implements dynamic frequency scaling for Panfrost GPUs using devfreq, OPP tables, optional speed-bin filtering, thermal cooling registration, and busy/idle accounting from job execution.

## Important APIs, Types, and Functions
Important functions are `panfrost_devfreq_init`, `panfrost_devfreq_fini`, `panfrost_devfreq_resume`, `panfrost_devfreq_suspend`, `panfrost_devfreq_record_busy`, `panfrost_devfreq_record_idle`, `panfrost_devfreq_target`, and `panfrost_devfreq_get_dev_status`. The devfreq profile uses `DEVFREQ_GOV_SIMPLE_ONDEMAND`.

## Control Flow
Initialization skips unsupported multi-supply platforms, reads an optional `speed-bin` nvmem cell, configures OPP regulators and tables, sets the recommended initial OPP, records the fastest rate, initializes simple_ondemand thresholds, registers devfreq, and optionally registers a cooling device. Runtime status snapshots lock the counters, fold time since the last update into busy or idle buckets, publish total/busy time, and reset the interval. Job submission and completion call busy/idle recorders to maintain `busy_count`.

## State and Persistence Behavior
`struct panfrost_devfreq` stores current and fast frequencies, devfreq/cooling pointers, governor data, OPP table presence, time buckets, last update time, and busy count protected by a spinlock.

## Dependencies and Integration Points
It depends on the clock framework, OPP/dev_pm_opp, nvmem, devfreq, devfreq cooling, and Panfrost job paths that call the busy/idle hooks. fdinfo uses `current_frequency` and `fast_rate`.

## Risks
Busy-count imbalance produces wrong utilization and warns on negative idle transitions. Multi-supply platforms silently run without devfreq. Optional OPP and speed-bin failures have different severity; treating a required nvmem error as optional would choose unsafe OPPs. Debug logging divides by `total_time / 100`, which assumes nonzero elapsed time.

## Test Signals
Exercise OPP table parsing, speed-bin variants, thermal cooling registration, suspend/resume, concurrent jobs, busy/idle balance under reset and timeout paths, fdinfo frequencies, and governor frequency changes under GPU load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.h

## Purpose
This header declares Panfrost devfreq state and lifecycle/accounting entry points.

## Important APIs, Types, and Functions
`struct panfrost_devfreq` contains devfreq and cooling handles, governor data, OPP table state, current/fast frequency, busy/idle timing buckets, last update timestamp, busy count, and a spinlock. It declares init/fini, suspend/resume, and busy/idle record functions.

## Control Flow
The header has no executable flow. It defines the interface used by device initialization, PM callbacks, job submission/completion, reset paths, and fdinfo reporting.

## State and Persistence Behavior
The struct is embedded in `struct panfrost_device`, so it persists for the device lifetime. Its timing fields are mutable runtime counters protected by `lock`.

## Dependencies and Integration Points
It includes devfreq, spinlock, and ktime headers and forward-declares Panfrost and cooling types. `panfrost_device.h` embeds it, while `panfrost_job.c` and `panfrost_device.c` use the function declarations.

## Risks
Callers must check whether devfreq was actually registered before assuming frequency scaling. The lock discipline around timing fields must be preserved because jobs can update utilization concurrently.

## Test Signals
Build coverage catches signature drift. Runtime tests should validate that job paths and PM paths can call the declared hooks when devfreq is present or skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.c

## Purpose
This file owns Panfrost device bring-up, teardown, power-management callbacks, GPU reset orchestration, reset/clock/regulator/power-domain setup, and exception-name lookup.

## Important APIs, Types, and Functions
Public functions are `panfrost_device_init`, `panfrost_device_fini`, `panfrost_device_reset`, `panfrost_exception_name`, and `panfrost_exception_needs_reset`. Internal setup covers reset controls, clocks, regulators, multi-power-domain links, runtime/system PM, and the exception table.

## Control Flow
Initialization creates locks/lists, attaches power domains, deasserts resets, enables clocks, initializes devfreq, optionally enables regulators if OPP did not take ownership, maps MMIO, initializes GPU, MMU, job manager, performance counters, and GEM. Failures unwind in reverse. Runtime resume optionally deasserts reset/enables clocks, resets the GPU stack, and resumes devfreq. Runtime suspend refuses non-idle job manager state, suspends devfreq and IRQs, powers off GPU blocks, and optionally disables clocks/asserts reset. System suspend/resume additionally handles platform PM feature bits and OPP regulator state.

## State and Persistence Behavior
The file mutates the device's locks, lists, reset/clock/regulator/domain handles, `iomem`, power-feature-dependent hardware state, IRQ suspension bits, address-space state through reset, and devfreq state.

## Dependencies and Integration Points
It coordinates all major Panfrost subsystems: GPU, MMU, job manager, GEM, devfreq, performance counters, reset controls, clocks, regulators, PM domains, runtime PM, and OPP.

## Risks
Initialization unwind order must mirror setup or clocks/regulators/IRQs can leak. Runtime suspend must only proceed when the job manager is idle. PM feature bits vary by compatible data, so wrong OF match data can disable rails or clocks incorrectly. Reset reinitializes GPU/MMU/JM state and must be synchronized with scheduler recovery.

## Test Signals
Signals include probe failure injection at each init stage, runtime autosuspend under idle and active jobs, system suspend/resume on all compatible PM feature combinations, reset after GPU faults, and exception-name coverage for fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.h

## Purpose
This header defines the central Panfrost device, feature, compatibility, per-file, MMU, and exception types shared by the driver.

## Important APIs, Types, and Functions
Key types are `struct panfrost_device`, `struct panfrost_features`, `struct panfrost_compatible`, `struct panfrost_mmu`, `struct panfrost_file_priv`, and `struct panfrost_engine_usage`. It defines PM feature bits, GPU quirks, component suspension bits, exception codes, address-space interrupt masks, helper predicates, and lifecycle/reset declarations.

## Control Flow
The header has inline flow for privilege checks, model comparison, Bifrost detection, exception fault classification, and reset work scheduling.

## State and Persistence Behavior
`struct panfrost_device` is the persistent DRM-device object and contains MMIO, IRQs, clocks, regulators, PM domains, feature registers, scheduler/job state, reset work, shrinker state, devfreq, cycle counter, and debugfs lists. `struct panfrost_file_priv` persists per DRM fd and owns an MMU context and JM contexts.

## Dependencies and Integration Points
It ties together DRM device/auth, DRM MM, GPU scheduler, regulator, PM, io-pgtable, devfreq, and job manager declarations. Most Panfrost `.c` files include it directly or indirectly.

## Risks
Because this header defines cross-subsystem shared state, layout or semantic changes have broad blast radius. Lock ownership for `as_lock`, `sched_lock`, shrinker locks, job locks, and debugfs locks must stay consistent. Exception values must match the UAPI and hardware encoding.

## Test Signals
Build coverage catches type drift. Runtime signals include correct fd private allocation/free, scheduler/debugfs/fdinfo access, MMU AS reuse, reset work scheduling, and fault classification in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.c

## Purpose
This is the Panfrost platform and DRM driver entry point. It defines the DRM UAPI ioctl handlers, file open/close lifecycle, fdinfo/debugfs reporting, probe/remove, sysfs profiling control, compatible data, and module registration.

## Important APIs, Types, and Functions
Important ioctls include get-param, create/mmap/wait/get-offset/madvise/set-label/sync/query BO, submit, and JM context create/destroy. Important lifecycle functions are `panfrost_open`, `panfrost_postclose`, `panfrost_probe`, and `panfrost_remove`. It also defines `panfrost_drm_driver`, compatible data tables, and the `unstable_ioctls` and `transparent_hugepage` module parameters.

## Control Flow
Probe allocates `struct panfrost_device` as a DRM device, reads compatible data and coherency, initializes shrinker state, calls device init, enables runtime PM/autosuspend, registers DRM, and registers the GEM shrinker. Open allocates per-file state, creates an MMU context, and opens job-manager contexts. Submit validates inputs, resolves output syncobj, JM context, incoming syncobjs, BO handles and mappings, initializes a scheduler job, pushes it, and attaches the output fence. Remove unregisters DRM, frees shrinker, disables runtime PM, and tears down the device.

## State and Persistence Behavior
Per-device state includes DRM registration, PM state, compatible policy, shrinker, profiling flag, and module parameters. Per-file state owns MMU and JM contexts plus engine usage counters. BO ioctls mutate GEM objects, labels, mappings, purgeability, and cache state.

## Dependencies and Integration Points
It integrates with DRM core ioctls, syncobjs, GEM handles, dma-resv, runtime PM, device tree, sysfs attributes, debugfs, Panfrost GEM/MMU/job/perfcnt subsystems, and the platform driver bus.

## Risks
UAPI validation is security-sensitive: padding, flags, handles, sync object counts, user pointers, and priority permissions must remain strict. Submit cleanup relies on reference ownership across scheduler jobs, BO mappings, syncobjs, and JM contexts. MADVISE only supports single-owner purgeable BOs. Compatible data drives PM behavior and platform quirks.

## Test Signals
Run userspace submit/create/wait/mmap/get-param paths, invalid ioctl fuzzing, syncobj dependency tests, PRIME/import query tests, JM context priority permission checks, fd close with in-flight jobs, runtime PM autosuspend, sysfs profiling toggles, and debugfs/fdinfo reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.h

## Purpose
This small header exposes the transparent hugepage module setting to Panfrost GEM code.

## Important APIs, Types, and Functions
It declares `extern bool panfrost_transparent_hugepage` when the header is included. No functions or types are defined.

## Control Flow
There is no executable flow. `panfrost_gem_init` reads the variable to decide whether to create a hugepage-enabled GEM mount when transparent hugepage support is configured.

## State and Persistence Behavior
The actual state is defined in `panfrost_drv.c` under `CONFIG_TRANSPARENT_HUGEPAGE` as a read-only module parameter. This header only provides access to that state.

## Dependencies and Integration Points
It connects the driver module parameter defined by the platform/DRM entry file to the GEM initialization implementation.

## Risks
The declaration is only valid when the corresponding definition is compiled; callers should keep use guarded consistently with `CONFIG_TRANSPARENT_HUGEPAGE`. Any future settings added here become cross-file driver configuration surface.

## Test Signals
Build with and without transparent hugepage support and boot with `panfrost.transparent_hugepage=0/1` to verify GEM initialization follows the setting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.c

## Purpose
This file creates Panfrost GPU devcoredumps when a job times out. It captures selected registers, active BO contents, physical page maps, and a trailer in the Panfrost dump format.

## Important APIs, Types, and Functions
The public entry point is `panfrost_core_dump`. Internal helpers are `panfrost_core_dump_header` and `panfrost_core_dump_registers`. `struct panfrost_dump_iterator` tracks headers and data offsets. The module parameter `dump_core` arms or disables one-shot dumping.

## Control Flow
On timeout, the job manager calls `panfrost_core_dump`. The function checks and clears the one-shot flag, computes file size from register dump, headers, job BO sizes, and optional BO page map, allocates vmalloc memory, fills the register header with job and GPU metadata, dumps registers adjusted for the job slot and address space, optionally builds a BO physical map, vmaps each BO, copies its contents, emits headers, appends a trailer, and hands the buffer to `dev_coredumpv`.

## State and Persistence Behavior
The only persistent local state is the module parameter. Dump contents are transient until accepted by devcoredump infrastructure. It reads job mappings, BO sg tables, GPU registers, and MMU/job slot state but does not mutate BO contents.

## Dependencies and Integration Points
It depends on Panfrost job, GEM, registers, and device state, DRM/Panfrost dump UAPI structures, `drm_gem_vmap`, sg page iteration, vmalloc, and Linux devcoredump.

## Risks
Dump size scales with BO size and may fail allocation. Missing sg tables or vmap failures mark BO dump entries invalid. It assumes PAGE_SIZE alignment for BOs. Dumping BO contents can expose user GPU memory to privileged devcoredump readers, so access policy matters.

## Test Signals
Induce GPU scheduler timeouts, verify one-shot dump behavior and manual rearm, decode with pandecode, test large BO allocation failure, BO vmap failure, and register slot/address-space offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.h

## Purpose
This header declares the Panfrost core dump entry point.

## Important APIs, Types, and Functions
It forward-declares `struct panfrost_job` and declares `void panfrost_core_dump(struct panfrost_job *job)`.

## Control Flow
There is no executable flow. The job timeout path includes this header and invokes the dump function with the timed-out job.

## State and Persistence Behavior
The header stores no state. The implementation reads job/device/BO state and emits devcoredump data.

## Dependencies and Integration Points
It is an integration point between the job manager and dump implementation while avoiding a full job header dependency for callers that only need the prototype.

## Risks
Signature drift between the declaration and implementation would break build. Callers must pass a live job whose BO and mapping arrays are still valid.

## Test Signals
Build coverage and timeout-driven dump generation validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_features.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_features.h

## Purpose
This header defines software feature bits and model-specific feature masks for supported Mali Midgard/Bifrost GPUs.

## Important APIs, Types, and Functions
`enum panfrost_hw_feature` lists feature flags such as jobchain disambiguation, XAFFINITY, flush reduction, protected mode, AArch64 MMU, TLS hashing, IDVS group size, and cache-clean safety. `hw_features_*` macros map GPU families to bitmasks. `panfrost_has_hw_feature` tests the runtime bitmap.

## Control Flow
There is no runtime flow beyond the inline bitmap test. `panfrost_gpu_init_features` consumes the masks when it matches a GPU model and populates `pfdev->features.hw_features`.

## State and Persistence Behavior
The header defines compile-time masks. Runtime feature state lives in `struct panfrost_features` in the device object.

## Dependencies and Integration Points
It depends on bitops and `panfrost_device.h`. GPU init, MMU selection, job submission, quirks, flush reduction, and reset logic use these feature predicates.

## Risks
Incorrect model masks can enable unsupported hardware paths or miss required workarounds. Feature names are driver-internal and must stay aligned with register/programming assumptions, not just marketing GPU names.

## Test Signals
Validate feature bitmaps in boot logs for each GPU model, exercise AArch64 MMU and flush-reduction paths only on advertised hardware, and compare userspace feature queries against expected model data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.c

## Purpose
This file implements Panfrost GEM buffer objects, per-file GPU virtual mappings, PRIME dma-buf integration, cache synchronization, labels, debugfs reporting, and optional transparent hugepage backing.

## Important APIs, Types, and Functions
Key entry points are `panfrost_gem_init`, `panfrost_gem_create_object`, `panfrost_gem_create`, `panfrost_gem_open`, `panfrost_gem_close`, `panfrost_gem_mapping_get/put`, `panfrost_gem_teardown_mappings_locked`, PRIME import/export callbacks, `panfrost_gem_sync`, label helpers, and debugfs BO printing.

## Control Flow
Object creation allocates shmem GEM, initializes mapping lists and labels, sets default cacheability, and tags heap/noexec/WB flags. GEM open allocates a `panfrost_gem_mapping`, assigns a VA range in the file MMU with executable alignment/color constraints, maps non-heap objects immediately, and links the mapping. Close unlinks and drops the mapping, which unmaps and removes the VA node at final ref. PRIME callbacks synchronize sg tables and vmap ranges for CPU/device access. Cache sync walks DMA sg entries over the requested range.

## State and Persistence Behavior
BO state includes shmem backing, optional per-2 MiB sg tables for heap faults, mapping list, GPU usecount, heap resident size, label string, cacheability flags, debugfs metadata, and madvise state inherited from shmem GEM. Mapping state includes VA node, MMU context, refcount, and active bit.

## Dependencies and Integration Points
It depends on DRM GEM shmem helpers, drm_mm, dma-buf, DMA mapping/cache APIs, Panfrost MMU, per-file private state, shrinker, debugfs, and the driver-wide transparent hugepage parameter.

## Risks
Mapping refcounts must stay balanced across handles, jobs, and close. Executable buffers must not cross 16 MiB and 4 GiB-sensitive boundaries. Heap BOs are fault-mapped lazily and cannot be CPU mmapped. Cache sync rejects imported buffers and must avoid stale data on coherent versus noncoherent devices. Label lifetime is protected by a mutex and const-free semantics.

## Test Signals
Test create/open/close, mmap restrictions for heap BOs, per-file VA reuse, job submission with shared BOs, PRIME import/export CPU access, cache flush/invalidate ranges, shrinker interaction, label ioctl/debugfs output, and transparent hugepage mount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.h

## Purpose
This header defines Panfrost GEM object and mapping structures plus the public GEM subsystem API.

## Important APIs, Types, and Functions
It defines `PANFROST_BO_LABEL_MAXLEN`, debugfs GEM state flags, `struct panfrost_gem_debugfs`, `struct panfrost_gem_object`, and `struct panfrost_gem_mapping`. It declares GEM create/import/open/close, mapping refcount helpers, shrinker hooks, label helpers, cache sync, and debugfs printing.

## Control Flow
The header has inline casts from `drm_gem_object` to `panfrost_gem_object` and from `drm_mm_node` to `panfrost_gem_mapping`. Other behavior is implemented in `.c` files.

## State and Persistence Behavior
The structs describe persistent BO state, including shmem base, sg tables, per-MMU mappings, GPU usecount, heap RSS, labels, flags, and debugfs metadata. Mapping structs persist while a BO is open in an MMU context or referenced by jobs.

## Dependencies and Integration Points
It integrates DRM shmem GEM, drm_mm, Panfrost MMU, Panfrost device/file state, shrinker, debugfs, and UAPI-visible BO labels/cache sync behaviors.

## Risks
Fields such as `gpu_usecount`, `heap_rss_size`, and `active` are consumed by shrinker, MMU, and job code; changing semantics can corrupt memory reclamation or GPU VA teardown. Locking around `mappings` and labels must be respected by callers.

## Test Signals
Build and runtime coverage across GEM creation, mapping, shrinker purge, MMU faults, job BO references, labels, debugfs, and PRIME paths validates the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem_shrinker.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem_shrinker.c

## Purpose
This file registers a memory shrinker for purgeable Panfrost shmem GEM objects.

## Important APIs, Types, and Functions
The public functions are `panfrost_gem_shrinker_init` and `panfrost_gem_shrinker_cleanup`. Internal callbacks are `panfrost_gem_shrinker_count`, `panfrost_gem_shrinker_scan`, and `panfrost_gem_purge`.

## Control Flow
The count callback try-locks the device shrinker lock and sums pages for purgeable objects on `pfdev->shrinker_list`. The scan callback iterates the same list until the scan budget is met, purging objects that are still purgeable and successfully locked. Purge refuses BOs in GPU use, locks mappings and reservation, tears down GPU mappings, calls `drm_gem_shmem_purge_locked`, and removes purged entries from the list.

## State and Persistence Behavior
It mutates `pfdev->shrinker`, `pfdev->shrinker_list`, BO mapping activity, shmem GEM pages/madv state, and heap/GPU mapping residency indirectly through teardown. It never blocks indefinitely because it uses trylocks in reclaim context.

## Dependencies and Integration Points
It integrates with Linux shrinker infrastructure, DRM shmem GEM purge helpers, Panfrost GEM mappings, MMU teardown, dma-resv locking, and the MADVISE ioctl that places objects on the shrinker list.

## Risks
Reclaim context lock ordering is delicate. Objects with active GPU use must not be purged. Mapping teardown before shmem purge is required to prevent GPU access to freed pages. Trylock failures reduce reclaim effectiveness under contention.

## Test Signals
Use memory pressure with MADV_DONTNEED BOs, jobs holding purgeable BO references, repeated MADV_WILLNEED/DONTNEED transitions, lock contention, and post-purge fault/access behavior to validate the shrinker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem_shrinker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.c

## Purpose
This file manages GPU block reset, IRQ handling, feature discovery, model/errata matching, power on/off of shader/tiler/L2 blocks, cycle/timestamp counters, and selected vendor quirks.

## Important APIs, Types, and Functions
Public functions include `panfrost_gpu_init`, `panfrost_gpu_fini`, `panfrost_gpu_soft_reset`, `panfrost_gpu_power_on/off`, `panfrost_gpu_suspend_irq`, cycle/timestamp read and refcount helpers, `panfrost_gpu_get_latest_flush_id`, and `panfrost_gpu_amlogic_quirk`. Internal logic includes `panfrost_gpu_init_features`, `panfrost_gpu_init_quirks`, and the GPU IRQ handler.

## Control Flow
Initialization soft-resets the GPU, reads feature registers, matches the GPU ID/revision to model tables, configures DMA masks, requests the GPU IRQ, and powers on blocks. Power-on programs shader/JM/tiler quirks, chooses a core mask, powers L2, shader, and tiler blocks, and polls ready registers. IRQ handling logs GPU faults, handles perfcnt sample/cache events, masks on fatal errors, and clears interrupts. Cycle counter get/put starts/stops the hardware counter with atomic and spinlock protection.

## State and Persistence Behavior
The file populates `pfdev->features`, GPU IRQ state, selected coherency, hw feature/issue bitmaps, cycle counter use count, and hardware power/config registers. Power state is volatile and restored after reset/runtime resume.

## Dependencies and Integration Points
It depends on Panfrost registers, feature/issue tables, perfcnt callbacks, runtime PM, DMA mask setup, platform IRQs, and device reset/PM code.

## Risks
Model table mistakes can apply wrong features or errata. Power polling timeouts leave hardware partially enabled. Multi-core-group support is limited to the first group. Cycle counter refcount imbalance can leave counters running. GPU faults mask interrupts and require recovery through reset paths.

## Test Signals
Boot logs for model/features/issues, GPU IRQ fault injection, perfcnt sampling, reset timeout tests, runtime suspend/resume, cycle counter UAPI queries, Amlogic quirk validation, and multi-core-group behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.h

## Purpose
This header declares the Panfrost GPU block interface for initialization, reset, power, IRQ suspend, counters, flush-id reading, and vendor quirks.

## Important APIs, Types, and Functions
It declares `panfrost_gpu_init/fini`, `panfrost_gpu_get_latest_flush_id`, `panfrost_gpu_soft_reset`, `panfrost_gpu_power_on/off`, `panfrost_gpu_suspend_irq`, cycle counter get/put/read, timestamp read, and `panfrost_gpu_amlogic_quirk`.

## Control Flow
There is no executable flow. Device init/PM/reset/job paths call these functions to control GPU hardware and read counters.

## State and Persistence Behavior
The header stores no state. Implementations mutate `struct panfrost_device` feature, IRQ, power, and cycle-counter fields and hardware registers.

## Dependencies and Integration Points
It is used by device init/reset, ioctl timestamp queries, job profiling, fdinfo, compatible data vendor hooks, and GPU PM code.

## Risks
Callers must hold or acquire runtime PM as appropriate before reading hardware registers. Counter get/put calls must remain balanced around jobs and timestamp reads.

## Test Signals
Build coverage plus runtime reset, timestamp, profiling, PM, and compatible quirk tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_issues.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_issues.h

## Purpose
This header enumerates hardware issues and errata masks for supported Mali GPU models and revisions.

## Important APIs, Types, and Functions
`enum panfrost_hw_issue` lists driver-relevant errata. `hw_issues_*` macros define common, model, and revision-specific bitmasks. `panfrost_has_hw_issue` tests a device's runtime issue bitmap.

## Control Flow
The only executable logic is the inline bitmap test. GPU feature initialization combines these masks after matching GPU ID/revision, and other subsystems branch on the resulting issue bits.

## State and Persistence Behavior
The header defines static masks. Runtime issue state is stored in `pfdev->features.hw_issues`.

## Dependencies and Integration Points
Issue predicates are consumed by GPU quirk programming, job submission flags, reset policy, MMU workarounds, performance counter behavior, and exception reset decisions.

## Risks
Errata data must match exact GPU revisions. Missing an issue can cause hangs, data corruption, or missing resets; falsely enabling an issue can reduce performance or change programming sequences incorrectly. The list is intentionally incomplete and includes only issues the driver uses.

## Test Signals
Validate boot logs against known GPU revisions, exercise code paths for issue-dependent flags, run conformance workloads on each model, and test fault/reset cases such as TTRX_3076 bus-fault recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_issues.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.c

## Purpose
This file implements the Panfrost job manager: DRM scheduler integration, hardware job submission, job IRQ handling, fences, reset recovery, profiling/accounting, and per-file JM context management.

## Important APIs, Types, and Functions
Key public functions are `panfrost_jm_init/fini/open/close`, `panfrost_jm_ctx_create/destroy/get/put/from_handle`, `panfrost_job_get_slot`, `panfrost_job_push`, `panfrost_job_put`, IRQ suspend/reset helpers, and `panfrost_jm_is_idle`. Internal pieces include Panfrost fences, scheduler ops, hardware submit, IRQ handlers, timeout handling, and reset work.

## Control Flow
Userspace submit creates a scheduler job elsewhere, then `panfrost_job_push` locks BO reservations, arms the scheduler job, adds implicit dependencies, queues it, and attaches write fences. Scheduler `run_job` creates a Panfrost fence and submits to hardware. Hardware submit resumes runtime PM, gets an MMU AS, records devfreq busy, writes job chain address/config/affinity/flush-id, enqueues in one of two hardware subslots, starts cycle counting if needed, and issues START. IRQ handling dequeues done or failed jobs, signals fences, releases AS/runtime PM/devfreq, requeues second-slot jobs when safe, or schedules reset. Timeouts produce devcoredumps and reset the GPU.

## State and Persistence Behavior
State includes per-slot schedulers, fence contexts/seqnos, `pfdev->jobs[slot][subslot]`, scheduled jobs list, reset work/pending flag, per-file JM context xarray, job refcounts, BO mapping refs, done/render fences, profiling timestamps, and engine usage counters.

## Dependencies and Integration Points
It integrates DRM GPU scheduler, DMA fences, dma-resv, runtime PM, Panfrost MMU AS allocation, devfreq, GPU counters, GEM mappings, devcoredump, reset code, UAPI JM context priority, and fdinfo accounting.

## Risks
Reset and IRQ paths are concurrency-heavy and must balance runtime PM, devfreq, MMU AS refs, cycle counter refs, job refs, and fences. Jobchain disambiguation controls whether two hardware slots can be used. Destroying JM contexts must hard-stop in-flight jobs without touching freed file state. Timeout handling must distinguish interrupt latency from real hangs.

## Test Signals
Run parallel fragment/vertex submissions, syncobj and implicit-fence tests, context destroy with in-flight jobs, high-priority permission checks, GPU timeout/reset, devfreq/cycle counter balance, fd close races, IRQ storm/fault injection, and scheduler debugfs inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.h

## Purpose
This header defines Panfrost job and job-manager context structures plus the job manager API used by ioctl, device, reset, and scheduler code.

## Important APIs, Types, and Functions
`struct panfrost_job` embeds `drm_sched_job` and stores device, MMU, JM context, fences, job chain address, requirements, flush id, BO/mapping arrays, render fence, and profiling fields. `NUM_JOB_SLOTS` is 3. `struct panfrost_jm_ctx` owns scheduler entities per slot. The header declares job push/put, slot selection, JM lifecycle, IRQ helpers, idle test, and context handle helpers.

## Control Flow
The header has no executable flow. It defines the data contract consumed by submit ioctls, scheduler callbacks, IRQ handlers, resets, dumps, and fd cleanup.

## State and Persistence Behavior
Jobs persist from ioctl creation until scheduler/free and IRQ completion drop all refs. JM contexts persist per DRM file until destroyed or file close, but jobs can hold refs after the userspace handle is removed.

## Dependencies and Integration Points
It includes Panfrost UAPI and DRM GPU scheduler headers. It is included by driver ioctl code, job implementation, dump code, and device state definitions.

## Risks
Field ownership is subtle: `engine_usage` may be nulled when a file context is destroyed, while jobs continue. BO and mapping arrays must be cleaned after scheduler completion. Any new job requirement bits must stay synchronized with ioctl validation and slot selection.

## Test Signals
Build coverage, submit/timeout/reset tests, context create/destroy, fd close races, and devcoredump generation validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.c

## Purpose
This file implements Panfrost GPU MMU contexts, page-table setup, GPU virtual address allocation support, map/unmap, address-space assignment and LRU reuse, lazy heap fault mapping, MMU IRQ handling, and context teardown.

## Important APIs, Types, and Functions
Public entry points are `panfrost_mmu_ctx_create/get/put`, `panfrost_mmu_map`, `panfrost_mmu_unmap`, `panfrost_mmu_as_get/put`, `panfrost_mmu_reset`, `panfrost_mmu_init/fini`, and `panfrost_mmu_suspend_irq`. Internal helpers configure Mali LPAE or AArch64 page tables, encode memory attributes, flush hardware ranges, map sg tables, translate faults to mappings, and allocate heap pages on page fault.

## Control Flow
Context creation chooses page-table format from compatible quirks and hardware features, initializes a 32 MiB-4 GiB drm_mm VA space with executable color adjustment, allocates io-pgtable ops, and stores hardware MMU config. BO mapping walks DMA sg entries and maps 4 KiB/2 MiB pages through io-pgtable, then flushes the GPU range if the AS is active. `as_get` either reuses an assigned address space, re-enables a previously faulty AS, picks a free AS, or evicts an idle LRU AS and programs hardware registers. MMU threaded IRQ handles page faults; heap faults allocate/map 2 MiB chunks, while unhandled faults disable the AS and mask its interrupts.

## State and Persistence Behavior
State includes per-context page tables, drm_mm VA allocator, AS number, AS refcount, hardware config, device AS allocation/fault masks, AS LRU list, heap BO sg tables/pages, and mapping active bits. Runtime PM gates hardware TLB flushes.

## Dependencies and Integration Points
It integrates io-pgtable, DRM MM, GEM shmem and heap BOs, DMA mapping, runtime PM, platform IRQs, Panfrost registers/features, device reset, and job manager AS get/put.

## Risks
AS allocation and LRU eviction are protected by `as_lock`; mistakes can assign one AS to multiple contexts. Heap fault mapping assumes 2 MiB alignment and can leak or double-own folios if partial population invariants fail. TLB flushes are skipped when runtime-suspended, relying on reprogramming later. Unhandled faults disable AS to kill jobs, so recovery depends on later AS get/reset.

## Test Signals
Test BO map/unmap, per-file VA allocation, executable boundary constraints, AS reuse under many clients, heap BO page faults, MMU fault logging, reset after AS_ACTIVE timeout, runtime suspend during mapping changes, and AArch64 page-table compatible quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.h

## Purpose
This header declares the Panfrost MMU mapping, context, address-space, reset, IRQ suspend, and lifecycle API.

## Important APIs, Types, and Functions
It forward-declares Panfrost device, GEM mapping, file private, and MMU types. It declares map/unmap, init/fini/reset/suspend IRQ, AS get/put, MMU context get/put/create functions.

## Control Flow
The header has no executable flow. Job submission uses AS get/put, GEM mapping uses map/unmap, file open/close uses context create/get/put, and device reset/PM uses reset and IRQ suspend declarations.

## State and Persistence Behavior
The header stores no state. Implementations mutate page tables, drm_mm VA spaces, AS assignment masks, mapping active bits, and hardware MMU registers.

## Dependencies and Integration Points
It is the boundary between GEM, job manager, device reset/PM, and MMU implementation. Keeping it narrow avoids exposing io-pgtable details to callers.

## Risks
Callers must pair context and AS references correctly. Mapping functions expect a valid `panfrost_gem_mapping` with an allocated VA node and live MMU context.

## Test Signals
Build coverage plus GEM open/close, job submit/completion, MMU fault handling, file close, and reset paths validate the declared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.h -->
