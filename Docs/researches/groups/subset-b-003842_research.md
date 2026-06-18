# subset-b-003842 CoreSight Research

Grouped research for the requested CoreSight source files. Each section preserves the source path in its title and is delimited for reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.c

## Purpose
`coresight-catu.c` implements the Arm CoreSight CATU, a helper device that lets a TMC-ETR sink consume a scatter-gather trace buffer through a CATU translation table. Its main roles are to build CATU-compatible 4 KiB translation-table pages over TMC scatter-gather pages, register CATU-backed `etr_buf_operations`, and program the CATU into either translate or pass-through mode when a CoreSight trace path is enabled.

## Important APIs, Types, And Functions
The file-private `struct catu_etr_buf` stores the allocated `tmc_sg_table` and table base DMA address (`sladdr`) attached to an `etr_buf`. `catu_get_table()` maps a trace-buffer offset to the CATU table page and optionally returns the DMA address of that table. `catu_populate_table()` fills all data-page entries and previous/next table links. `catu_init_sg_table()` allocates the TMC scatter-gather table and populates it.

The ETR buffer operations are `catu_alloc_etr_buf()`, `catu_free_etr_buf()`, `catu_sync_etr_buf()`, and `catu_get_data_etr_buf()`, exported to TMC through `tmc_etr_set_catu_ops()`. The CoreSight helper callbacks are `catu_enable()` and `catu_disable()`, backed by `catu_enable_hw()` and `catu_disable_hw()`. Probe is shared between AMBA and ACPI/platform entry points via `__catu_probe()`.

## Control Flow
Module init registers both AMBA and platform drivers, then installs CATU ETR buffer ops. Probe enables CoreSight clocks, maps registers, derives a DMA mask from `CORESIGHT_DEVID`, loads CoreSight platform topology, clears stale self-claim tags, and registers a helper device with subtype `CORESIGHT_DEV_SUBTYPE_HELPER_CATU`.

When the TMC layer allocates an ETR buffer in CATU mode, `catu_alloc_etr_buf()` finds the CATU helper attached to the TMC, allocates the CATU private buffer, creates CATU tables, marks the `etr_buf` as `ETR_MODE_CATU`, and uses `CATU_DEFAULT_INADDR` as the synthetic ETR input address. On path enable, `catu_enable_hw()` waits for READY, claims the device, finds the upstream sysmem ETR, and asks it for the active buffer. If the ETR buffer is CATU-backed, CATU is programmed with `CATU_MODE_TRANSLATE`, `CATU_OS_AXICTRL`, `SLADDR`, and `INADDR`; otherwise it is programmed in pass-through mode. Disable clears CONTROL, disclaims the device, and waits for READY again.

## State And Persistence
Runtime state is in `struct catu_drvdata`: clock handles, MMIO base, CoreSight device, IRQ number, and a raw spinlock. Enable state is tracked through `csdev->refcnt`; hardware is only programmed for the first enable and only disabled on the final disable. CATU table/data state lives in TMC-owned `tmc_sg_table` objects attached to `etr_buf->private` and is freed through the ETR buffer operation. Trace-buffer read state (`etr_buf->offset` and `etr_buf->len`) is recomputed in `catu_sync_etr_buf()` from hardware RRP/RWP values.

## Dependencies And Integration Points
The driver depends on CoreSight helper-device registration, TMC ETR scatter-gather helpers, DMA mapping, runtime PM, AMBA discovery, and ACPI/platform discovery. It integrates with path enable/disable through CoreSight helper ops and with the TMC ETR allocation path through `tmc_etr_set_catu_ops()`. Management attributes expose CATU registers under a `mgmt` sysfs group.

## Risks
The table generator assumes CATU 4 KiB table/data pages and a 1 MiB addressable range per CATU table. Incorrect buffer sizing, page alignment, or table-link programming would corrupt trace capture. `catu_enable_hw()` claims the CATU before `tmc_etr_get_buffer()` returns; the error path returns directly if that call fails, which is worth checking against claim-leak expectations. `catu_sync_etr_buf()` subtracts hardware addresses from `etr_buf->hwaddr`; invalid RRP/RWP values could produce bogus offsets. DMA mask derivation defaults unknown hardware to 40 bits, which is pragmatic for TMC-ETR but may hide unusual platform constraints.

## Test Signals
Useful validation includes CATU probe on AMBA and ACPI/platform systems, sysfs `mgmt` register reads, ETR allocation with and without CATU, wrap-around trace-buffer sync, trace extraction through `tmc_sg_table_get_data()`, runtime PM suspend/resume, and failure injection for SG allocation and `tmc_etr_get_buffer()`. Hardware tests should verify translate mode actually maps discontinuous pages and pass-through mode still allows non-CATU ETR operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.h

## Purpose
`coresight-catu.h` defines the register layout, bit fields, CATU driver state, typed register accessors, and helper-device identification predicate used by the CATU implementation.

## Important APIs, Types, And Functions
The register offsets cover control, mode, AXI attributes, IRQ enable, base table address (`SLADDR`), input address (`INADDR`), status, and device architecture. Bit definitions include `CATU_CONTROL_ENABLE`, translate/pass-through modes, AXI `ARCACHE`/`ARPROT` construction helpers, OS AXI defaults, status bits, and IRQ enable constants.

`struct catu_drvdata` is the shared per-device state: programming and AT clocks, MMIO base, registered CoreSight device, IRQ, and raw spinlock. `CATU_REG32()` and `CATU_REG_PAIR()` generate inline accessors over the CoreSight `csdev_access` abstraction, so the C file can use typed `catu_read_*()` and `catu_write_*()` helpers without open-coded offsets. `coresight_is_catu_device()` checks Kconfig, CoreSight device type, and helper subtype.

## Control Flow
The header itself has no runtime control flow. It shapes the C file by guaranteeing all register accesses go through `csdev_access_relaxed_*()` helpers and by providing the predicate used by other CoreSight/TMC code to detect a CATU helper.

## State And Persistence
No state is persisted in the header, but `struct catu_drvdata` is the in-memory state carried from probe through enable, disable, runtime PM, and removal. The generated accessor helpers depend on `drvdata->csdev` being initialized before use.

## Dependencies And Integration Points
The header depends on `coresight-priv.h` for CoreSight access helpers and device type constants. It is consumed by the CATU C file and by any code that needs to test whether a `coresight_device` is a CATU helper.

## Risks
Accessor macros hide offset and width decisions, so register definitions must be correct. `coresight_is_catu_device()` returns false when `CONFIG_CORESIGHT_CATU` is disabled, which protects generic code but means CATU-dependent paths must handle absence cleanly.

## Test Signals
Compile coverage with and without `CONFIG_CORESIGHT_CATU` should exercise the inline predicate. Hardware register smoke tests should confirm the generated 32-bit and paired 64-bit accessors read/write the expected CATU registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-afdo.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-afdo.c

## Purpose
`coresight-cfg-afdo.c` provides preloaded CoreSight system-configuration descriptors for ETMv4 AutoFDO-style periodic trace capture. When ETMv4 source support is enabled, it defines a reusable `strobing` feature and an `autofdo` configuration that applies that feature with a set of preset mark/space ratios.

## Important APIs, Types, And Functions
The file declares `strobe_params` with `window` and `period` defaults. `strobe_regs` describes ETMv4 resource selector, sequencer, counter, reload, and view-inst register programming using `struct cscfg_regval_desc`. Some entries are resources, some save volatile counter values on disable, and reload registers use `CS_CFG_REG_TYPE_VAL_PARAM` to bind values to feature parameters.

`struct cscfg_feature_desc strobe_etm4x` is the feature export. `struct cscfg_config_desc afdo_etm4x` is the configuration export; it references `strobing`, declares nine presets, and supplies `afdo_presets`.

## Control Flow
There is no executable control flow beyond static descriptor construction. The CoreSight syscfg preload path imports these descriptors through `coresight-cfg-preload.c`, after which the generic configuration loader validates feature references, matches features to ETMv4 devices, and programs them through per-device config support.

## State And Persistence
The descriptors are static module data. Runtime state is created elsewhere when these descriptors are loaded into `cscfg_feature_csdev` and `cscfg_config_csdev` instances. The preset matrix is immutable and indexed by the generic config code when a perf/user configuration chooses a preset.

## Dependencies And Integration Points
This file depends on `coresight-config.h` for descriptor types and on ETMv4 config register definitions from `coresight-etm4x-cfg.h`. It is compiled only when `CONFIG_CORESIGHT_SOURCE_ETM4X` is available and is exposed through `coresight-cfg-preload.h`.

## Risks
Descriptor correctness is critical: wrong ETMv4 offsets, resource IDs, masks, or parameter indexes will program trace sources incorrectly. The `afdo_presets` comments describe varying period while holding window constant, but the second parameter values are small multipliers/period settings; tests should confirm generic code interprets them exactly as intended for ETMv4 counter reload values.

## Test Signals
Expected tests include descriptor load success, configfs/syscfg visibility of `strobing` and `autofdo`, ETMv4 feature matching, each preset index programming the counter reload registers, and trace captures showing periodic windows. Negative tests should verify builds without ETMv4 exclude these exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-afdo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.c

## Purpose
`coresight-cfg-preload.c` is the initialization bridge that registers built-in CoreSight feature and configuration descriptors with the system configuration manager.

## Important APIs, Types, And Functions
The file defines `preload_feats[]` and `preload_cfgs[]`, conditionally including ETMv4 descriptors such as `strobe_etm4x`, `gen_etrig_etm4x`, `afdo_etm4x`, and `pstop_etm4x`. `preload_owner` identifies the load owner as `CSCFG_OWNER_PRELOAD`. The single exported function, `cscfg_preload(void *owner_handle)`, records the owner handle and calls `cscfg_load_config_sets()`.

## Control Flow
CoreSight syscfg initialization calls `cscfg_preload()`. The function updates the owner context, then passes the null-terminated feature/config arrays into the loader. Conditional compilation keeps the arrays empty except for NULL sentinels when ETMv4 support is absent.

## State And Persistence
The persistent state is the static owner record and the static descriptor pointer arrays. Loaded runtime objects and configfs/syscfg state are owned by the syscfg subsystem after `cscfg_load_config_sets()` succeeds.

## Dependencies And Integration Points
This file depends on `coresight-cfg-preload.h` for descriptor declarations, `coresight-config.h` for descriptor types, and `coresight-syscfg.h` for the loader API and owner metadata. It integrates built-in descriptor files with the dynamic configuration-management layer.

## Risks
Any descriptor referenced here must be defined under matching Kconfig conditions; otherwise builds can fail or the preload arrays can reference unavailable symbols. Load-order issues would affect whether built-in configurations appear at CoreSight initialization.

## Test Signals
Boot-time syscfg initialization should show the preloaded configurations and features when ETMv4 is enabled, and no invalid references when ETMv4 is disabled. Failure injection around `cscfg_load_config_sets()` should propagate errors to the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.h

## Purpose
`coresight-cfg-preload.h` declares the built-in CoreSight configuration and feature descriptors that can be preloaded by the syscfg subsystem.

## Important APIs, Types, And Functions
Under `CONFIG_CORESIGHT_SOURCE_ETM4X`, it declares the ETMv4 feature descriptors `strobe_etm4x` and `gen_etrig_etm4x`, plus configuration descriptors `afdo_etm4x` and `pstop_etm4x`. There are no functions or types defined in this header.

## Control Flow
The header affects compile-time visibility only. `coresight-cfg-preload.c` includes it to populate preload arrays with descriptors from `coresight-cfg-afdo.c` and `coresight-cfg-pstop.c`.

## State And Persistence
There is no direct state. The declared symbols refer to static descriptor objects in their defining C files.

## Dependencies And Integration Points
The header relies on the ETMv4 source Kconfig guard to keep declarations aligned with descriptor definitions. It is part of the preload integration contract between built-in descriptor providers and the syscfg loader.

## Risks
The header has no include guard in this source copy; repeated inclusion is currently harmless because it only contains extern declarations under a Kconfig guard, but an include guard would reduce future fragility. Any mismatch between declarations and definitions would break builds.

## Test Signals
Build testing with ETMv4 enabled and disabled is the primary signal. Preload tests indirectly exercise these declarations by verifying all declared descriptors are loadable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-preload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-pstop.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-pstop.c

## Purpose
`coresight-cfg-pstop.c` defines an ETMv4 preloaded configuration named `panicstop`. It programs ETM resources to generate an external trigger when execution reaches the kernel `panic` symbol, allowing trace infrastructure to stop or react around panic handling.

## Important APIs, Types, And Functions
`gen_etrig_params` contains one parameter, `address`, defaulted to `(u64)panic`. `gen_etrig_regs` programs an ETMv4 resource selector, a 64-bit address comparator driven by the parameter, comparator attributes, and `TRCEVENTCTL0R` to route comparator output to driver external output 0. `gen_etrig_etm4x` describes the `gen_etrig` feature. `pstop_etm4x` describes the `panicstop` configuration and references `gen_etrig`.

## Control Flow
Like the AFDO descriptor file, this file is declarative. At syscfg preload time, `coresight-cfg-preload.c` supplies the feature/config descriptors to the loader. At activation time, generic configuration code updates ETMv4 driver register storage so the hardware is programmed when the ETM source is enabled.

## State And Persistence
Descriptor state is static. The default panic address is captured at build/runtime link time through the `panic` symbol. Per-device runtime copies of register descriptors and parameters are owned by the generic config subsystem after load.

## Dependencies And Integration Points
The file depends on ETMv4 register definitions and `coresight-config.h`. It also depends on the global kernel `panic` symbol being valid as a match address. It integrates with ETMv4 external trigger routing and the preloaded syscfg path.

## Risks
Address matching for `panic` is architecture, KASLR, and symbol-reachability sensitive. The comparator attribute value `0xf00` and event control value must match ETMv4 expectations; mistakes can either never trigger or trigger on the wrong context. The configuration has no presets and one parameter, so user updates to the address should be validated by the generic config interface.

## Test Signals
Tests should verify `panicstop` appears as a preloaded configuration, loads into ETMv4 devices, programs a 64-bit address comparator, and can be activated without disturbing normal ETM programming. Hardware validation would use a controlled function address rather than forcing a real panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cfg-pstop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.c

## Purpose
`coresight-config.c` implements generic per-device programming helpers for CoreSight system configurations and features. It translates descriptor values and user/preset parameters into driver-owned register storage when a configuration is enabled, and saves selected register values when disabled.

## Important APIs, Types, And Functions
`cscfg_set_reg()` writes a configured register value to a driver storage location, supporting 64-bit values and 32-bit masked updates. `cscfg_save_reg()` copies driver storage back into a descriptor instance for registers marked `CS_CFG_REG_TYPE_VAL_SAVE`. `cscfg_init_reg_param()` binds a feature parameter to the register instance it controls and initializes the register from the parameter value.

`cscfg_reset_feat()` restores feature parameter and register instances from static descriptors. `cscfg_update_presets()` maps a selected preset row across the ordered feature parameter list. `cscfg_update_curr_params()` updates parameter-backed registers from current per-device parameter values. The public APIs are `cscfg_csdev_enable_config()` and `cscfg_csdev_disable_config()`.

## Control Flow
Feature load code elsewhere creates `cscfg_feature_csdev` and `cscfg_config_csdev` objects with pointers into driver register storage. On enable, `cscfg_csdev_enable_config()` either applies a preset or current parameter values, then calls `cscfg_prog_config(..., true)`. That iterates all features in the config and calls `cscfg_set_on_enable()`, which takes the device driver spinlock and copies all register values into driver storage. On disable, `cscfg_csdev_disable_config()` calls `cscfg_save_on_disable()` for each feature to preserve marked values.

## State And Persistence
The file does not allocate global state. It mutates runtime feature/config instances and the target driver register storage they reference. Parameter current values persist in `cscfg_parameter_csdev`; saved register values persist in each `cscfg_regval_csdev.reg_desc` for later inspection or re-enable.

## Dependencies And Integration Points
This file depends on `coresight-config.h` for data structures and `coresight-priv.h` for device context. It is generic infrastructure used by device-specific feature loaders, especially ETMv4 configuration support. Locking is delegated to each feature instance through `feat_csdev->drv_spinlock`.

## Risks
The generic code trusts earlier load-time validation for parameter indexes and driver register pointers. Bad descriptors can write through invalid pointers or apply 32-bit values to 64-bit storage. Preset ordering is positional across feature parameters, so changing feature order or parameter count without updating `nr_total_params` and preset arrays will silently misconfigure hardware. Lock coverage protects driver storage but not broader config activation policy.

## Test Signals
Unit-style tests should cover masked writes, 64-bit writes, saved registers, parameter binding, preset bounds, no-preset current parameters, and multi-feature parameter ordering. Integration tests should activate AFDO/panicstop configurations and verify resulting ETMv4 programmed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.h

## Purpose
`coresight-config.h` defines the generic data model for CoreSight system configurations: feature descriptors, configuration descriptors, per-device feature/config instances, register value descriptors, parameter instances, and feature load operations.

## Important APIs, Types, And Functions
Register flags describe standard/resource registers, parameter-backed values, masks, 64-bit values, and save-on-disable behavior. Match flags select device classes such as all sources or ETMv4 sources. `struct cscfg_parameter_desc` describes a named parameter. `struct cscfg_regval_desc` combines a compact bitfield register identity with value/mask/parameter-index storage.

`struct cscfg_feature_desc` defines a reusable feature and its register/parameter descriptors. `struct cscfg_config_desc` defines a system configuration that references features and may provide presets. Runtime structures `cscfg_regval_csdev`, `cscfg_parameter_csdev`, `cscfg_feature_csdev`, and `cscfg_config_csdev` bind descriptors to a specific `coresight_device` and its driver storage. `struct cscfg_csdev_feat_ops` lets devices load compatible features. Public helper prototypes cover enable, disable, and feature reset.

## Control Flow
The header has no executable control flow, but it encodes the lifecycle: descriptors are loaded into runtime per-device instances; configs reference loaded features; activation copies parameter/preset values to driver storage; disable can save volatile register state.

## State And Persistence
Descriptor objects are typically static or dynamically loaded metadata. Runtime instances persist per CoreSight device and track current parameter values, whether a config is enabled, and active counts. Config descriptors also carry configfs-related fields and an `available` flag used by multi-stage loading.

## Dependencies And Integration Points
The header depends on `linux/coresight.h`, configfs-visible `struct config_group`, and kernel list/dev-ext-attribute types. It is shared by descriptor providers, syscfg loading code, device-specific feature loaders, and generic config programming code.

## Risks
The compact bitfield layout restricts offsets and hardware info to 12 bits each; descriptors for larger offset spaces would not fit. `struct cscfg_config_csdev` uses a flexible array of feature pointers, so allocation size must be exact. The preset limit is tied to perf event config field width, making ABI changes non-local.

## Test Signals
Compile coverage across config providers is important. Runtime tests should validate descriptor load/unload, configfs exposure, preset limits, active counts, flexible-array allocation, and device match filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-core.c

## Purpose
`coresight-core.c` is the central CoreSight framework implementation. It registers the CoreSight bus, tracks devices and topology, resolves paths from sources to sinks, manages helper devices, exposes common claim/register helpers, coordinates runtime PM references, integrates CTI associations, initializes perf/syscfg support, and handles panic-time synchronization.

## Important APIs, Types, And Functions
Global state includes `coresight_mutex`, per-CPU default sinks, a device-name index list, and optional CTI association callbacks. Claim helpers (`coresight_claim_device*()`, `coresight_disclaim_device*()`, `coresight_clear_self_claim_tag*()`) protect CoreSight devices from external debug agents using claim tags. Topology helpers include `coresight_add_helper()`, `coresight_find_input_type()`, `coresight_find_output_type()`, orphan connection fixup, and connection removal.

Path management is implemented by `_coresight_build_path()`, `coresight_build_path()`, `coresight_release_path()`, `coresight_enable_path()`, and `coresight_disable_path()`. Sink/source utilities include default sink discovery, sink lookup by ID, per-CPU sink setters/getters, trace ID assignment, and source pause/resume wrappers. Registration is handled by `coresight_register()` and `coresight_unregister()`. Common driver helpers include `coresight_alloc_device_name()`, `coresight_init_driver()`, `coresight_remove_driver()`, `coresight_etm_get_trace_id()`, and `coresight_get_enable_clocks()`.

## Control Flow
Module init registers the CoreSight bus, initializes ETM perf support, installs a panic notifier, and initializes syscfg. Individual drivers call `coresight_register()` with a descriptor; registration creates a `coresight_device`, registers it on the bus, creates perf sink links and connection sysfs groups, fixes orphan connections, and notifies CTI association code. Unregistration removes CTI associations, sysfs links, topology references, platform data, and the device.

Path construction recursively walks output connections from source to sink, handles per-CPU source-to-sink shortcuts, powers and pins each device/helper through runtime PM and module references, and builds a source-to-sink list. Path enable iterates reverse order, enabling helpers first, then sinks and links; sources are enabled by sysfs/perf callers. Errors unwind already-enabled components. Disable skips the first source node, disables sinks/links, then adjacent helpers; `coresight_disable_source()` separately disables source helpers.

## State And Persistence
Core state is in registered `coresight_device` objects, topology connection arrays, per-device default sink cache, refcounts, bus registration, and per-prefix name index lists keyed by firmware node. Runtime PM/module references are acquired for active paths and released by `coresight_release_path()`. Panic sync visits all enabled devices and invokes optional panic ops.

## Dependencies And Integration Points
This file is the integration hub for AMBA/platform drivers, firmware graph data, CoreSight sysfs/perf helpers, CTI, syscfg, trace ID allocation, panic notifiers, runtime PM, clocks, and device links. Device-specific drivers depend on its exported registration, path, claim, timeout, access, and clock APIs.

## Risks
Topology handling must account for probe ordering; orphan fixup and helper dynamic connections are therefore sensitive to locking and fwnode lifetime. Path enable/disable order matters because enabling a sink/link can disrupt existing sessions if unwound incorrectly. Claim-tag races with external debuggers intentionally fail with `-EBUSY`, but stale or invalid tag states can block tracing. Name-index storage persists until module exit, so failed allocations leave lists for cleanup later. Recursive graph traversal assumes firmware topology has no harmful cycles.

## Test Signals
Key tests include mixed probe orders, hot-unplug/unregister, helper association before/after primary devices, default sink selection, path build/release refcount balance, sysfs and perf enable paths, trace ID allocation, runtime PM counts, external claim-tag contention, and panic notifier execution. KASAN/lockdep runs are useful around orphan fixup and connection removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cpu-debug.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cpu-debug.c

## Purpose
`coresight-cpu-debug.c` implements the CoreSight CPU external debug module driver. It samples per-CPU debug registers, especially EDPCSR, during panic handling and exposes a debugfs knob to keep debug power domains enabled or disabled.

## Important APIs, Types, And Functions
`struct debug_drvdata` stores the MMIO base, clock, associated CPU, feature-presence flags, sampled register values, and device pointer. `debug_init_arch_data()` runs on the target CPU to read EDDEVID/EDDEVID1 and determine whether PC sampling, context ID, virtual context, and PC offset handling are implemented. `debug_read_regs()` unlocks CoreSight/debug registers, requests CPU debug power, samples EDPCSR and related registers, and restores EDPRCR. `debug_dump_regs()` formats the sampled state. `debug_adjust_pc()` handles 64-bit direct PC composition or 32-bit Arm/Thumb offset adjustment.

The panic notifier is `debug_notifier_call()`. User control is through debugfs file operations for `coresight_cpu_debug/enable`. Probe/remove are shared between AMBA and platform paths through `__debug_probe()` and `__debug_remove()`.

## Control Flow
Probe enables clocks, resolves the CPU from firmware, maps registers, stores per-CPU drvdata, calls target-CPU architecture initialization, rejects devices without EDPCSR sampling, initializes the global debugfs/notifier on the first device, and drops runtime PM if debugging is disabled. The enable debugfs write powers all present CPU debug devices; disable drops them. On panic, the notifier takes `debug_lock` opportunistically, checks `debug_enable`, loops possible CPUs, reads registers for each initialized CPU debug block, and emits emergency logs.

## State And Persistence
State is stored per CPU in `DEFINE_PER_CPU(struct debug_drvdata *, debug_drvdata)`, plus global `debug_count`, `debug_enable`, `debug_lock`, and the debugfs directory. Runtime PM references keep debug blocks powered while enabled. Sampled register fields are overwritten on each panic/read pass.

## Dependencies And Integration Points
The driver depends on CoreSight register locking macros, CPU topology lookup, AMBA/platform probing, runtime PM, clocks, panic notifiers, debugfs, SMP calls, and low-level polling. It does not register as a trace path component; it is diagnostic infrastructure adjacent to CoreSight.

## Risks
Accessing debug registers when the CPU power domain is off or the OS double lock is set can lock up hardware; the code mitigates this with EDPRSR checks and power-up requests. Panic-notifier execution must avoid blocking, hence `mutex_trylock()`. Runtime PM refcount rollback in enable failure paths is important. PC adjustment for 32-bit instruction state is architecture-specific and can be implementation-defined for misaligned samples.

## Test Signals
Tests should cover AMBA and platform probe, CPU association failures, missing EDPCSR rejection, debugfs enable/disable refcounting, runtime PM suspend/resume, panic notifier output, powered-off CPU behavior, and 32-bit Thumb/Arm PC adjustment. Fault injection for `pm_runtime_get_sync()` and `smp_call_function_single()` should verify rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cpu-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu-core.c

## Purpose
`coresight-ctcu-core.c` implements the Qualcomm CoreSight TMC Control Unit helper. It programs per-ETR ATID filter registers so a TMC ETR sink accepts or rejects trace streams based on CoreSight trace ID bits.

## Important APIs, Types, And Functions
Platform configuration is described by `ctcu_etr_config` arrays; this file provides SA8775P offsets for two ETR ports. `ctcu_program_atid_register()` unlocks the device, sets or clears one trace-ID bit in an ATID register, and relocks it. `__ctcu_set_etr_traceid()` validates port configuration and trace ID, applies a per-port/per-trace-ID reference count, and only touches hardware on 0-to-1 or 1-to-0 transitions. `ctcu_get_active_port()` maps the active sink connection to a CTCU destination port. `ctcu_enable()` and `ctcu_disable()` are CoreSight helper callbacks.

## Control Flow
Probe allocates a CoreSight helper device name, loads CoreSight platform data, maps registers, enables clocks, copies SoC match data into `drvdata->atid_offset[]`, initializes the spinlock, and registers a helper subtype `CORESIGHT_DEV_SUBTYPE_HELPER_CTCU`. Runtime PM is enabled by the platform wrapper. During path enable, CoreSight helper handling calls `ctcu_enable()`, which extracts the path sink and assigned trace ID, finds the sink's active CTCU port, and sets the corresponding ATID bit. Disable clears the bit when the reference count drops to zero.

## State And Persistence
`struct ctcu_drvdata` stores MMIO base, APB clock, CoreSight device, spinlock, ATID offsets, and `traceid_refcnt[ETR_MAX_NUM][CORESIGHT_TRACE_ID_RES_TOP]`. Reference counts preserve correct behavior when multiple paths use the same trace ID and sink port. Hardware ATID state persists while the device is powered and is reconstructed by future enables.

## Dependencies And Integration Points
The driver depends on CoreSight helper topology, trace ID allocation, runtime PM, OF match data, clocks, and CoreSight lock macros. It integrates specifically with ETR sinks connected through firmware-described CTCU ports.

## Risks
`__ctcu_set_etr_traceid()` uses an unsigned 8-bit refcount; an unmatched disable can underflow before assignment and may program hardware incorrectly if call ordering is broken. The bounds check uses `reg_offset - atid_offset > CTCU_ATID_REG_SIZE`; exact end-offset semantics should be reviewed because the register window is four 32-bit registers. The `port_num` field from match data is not used when copying offsets; current code assumes array index equals port number.

## Test Signals
Tests should validate OF probe on SA8775P, helper association with ETR paths, trace ID bit set/clear for each ETR port, repeated enable/disable refcounting, invalid trace ID rejection, invalid port rejection, and runtime PM suspend/resume. Hardware trace should confirm ETR filtering changes when ATID bits are toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu.h

## Purpose
`coresight-ctcu.h` defines the private data structures for the Qualcomm CTCU helper driver and the maximum number of ETR ports it supports.

## Important APIs, Types, And Functions
`ETR_MAX_NUM` caps a single CTCU at two ETR devices. `struct ctcu_etr_config` describes the ATID0 register offset and connected CTCU port number for one ETR. `struct ctcu_config` groups SoC-specific ETR configurations. `struct ctcu_drvdata` holds MMIO base, APB clock, device/CoreSight handles, spinlock, ATID offsets, and per-port/per-trace-ID reference counts.

## Control Flow
The header has no runtime control flow. The CTCU core file uses these structures during probe, helper enable, and helper disable.

## State And Persistence
The critical state is `traceid_refcnt`, sized by `CORESIGHT_TRACE_ID_RES_TOP`, which mirrors the hardware ATID filter bits and prevents premature clearing when more than one path uses the same trace ID on the same ETR.

## Dependencies And Integration Points
The header includes `coresight-trace-id.h` for trace ID capacity. It is private to the CTCU implementation and its SoC match data.

## Risks
The hard-coded `ETR_MAX_NUM` must match all supported SoCs. If future hardware has more than two ETRs, both arrays and probe validation must be updated. The `u8` refcount constrains maximum simultaneous users per trace ID.

## Test Signals
Compile and probe tests should verify the array sizes, SoC config validation, and trace ID reference-count indexing. Future SoC additions should include tests for nontrivial port numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-ctcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-core.c

## Purpose
`coresight-cti-core.c` implements the Arm CoreSight Cross Trigger Interface helper. It manages CTI hardware programming, CoreSight helper enable/disable, trigger/channel operations, CTI-to-device associations, and AMBA driver registration.

## Important APIs, Types, And Functions
`ect_net` tracks all CTI devices; `ect_mutex` protects that list. `cti_write_all_hw_regs()` writes cached CTI trigger, gate, ASIC, and app-set registers to hardware while enabling the CTI. `cti_enable_hw()` and `cti_disable_hw()` claim/disclaim hardware and maintain `enable_req_count`. Register access helpers include `cti_read_single_reg()`, `cti_write_single_reg()`, and `cti_write_intack()`.

Metadata functions include `cti_set_default_config()`, `cti_allocate_trig_con()`, `cti_add_connection_entry()`, and `cti_add_default_connection()`. Programming APIs exposed to sysfs are `cti_channel_trig_op()`, `cti_channel_gate_op()`, and `cti_channel_setop()`. Association callbacks `cti_add_assoc_to_csdev()` and `cti_remove_assoc_from_csdev()` integrate with CoreSight registration.

## Control Flow
Probe maps the AMBA resource, initializes CTI device metadata, reads hardware DEVID to set max triggers/channels/default gates, obtains platform connection data, chooses a CPU-bound or system CTI name, creates dynamic sysfs groups, clears stale self-claim tags, registers as helper subtype `ECT_CTI`, adds itself to `ect_net`, and fixes associations to already-registered CoreSight devices. CoreSight core calls CTI association callbacks whenever other devices register/unregister, allowing CTIs declared before their associated devices to be connected later.

On helper enable, CTI is claimed and all cached registers are written if it was inactive; subsequent enables increment a refcount. Disable decrements and only disables hardware at zero. Sysfs channel operations update cached register state under the spinlock and write through if active.

## State And Persistence
Per-device state is in `struct cti_drvdata`, especially `ctidev.trig_cons` and `config`. The config cache persists trigger/channel programming across inactive periods so enabling can restore it. `enable_req_count` tracks active users. Association state persists as CoreSight helper links and CTI sysfs cross-links.

## Dependencies And Integration Points
The driver depends on AMBA discovery, CoreSight helper registration, firmware/platform connection parsing from `coresight-cti-platform.c`, dynamic sysfs creation from `coresight-cti-sysfs.c`, CoreSight claim tags, and optional CTI association callbacks in the core.

## Risks
Reference-count imbalance can leave CTI enabled or return `-EINVAL` on disable. Trigger filtering prevents unsafe outputs such as PE debug request, but disabling filters via sysfs can expose disruptive signals. Association fixup depends on firmware node names and sysfs link success; failures leave `con_dev` NULL. Hardware max trigger/channel values from DEVID are trusted after clamping trigger count.

## Test Signals
Tests should cover probe with v8 architectural, implementation-defined, and default connections; dynamic sysfs group creation; channel attach/detach/gate/app operations while inactive and active; enable/disable refcounting; CTI association before and after associated CoreSight device registration; removal cleanup; and lockdep coverage around sysfs/hardware paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-platform.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-platform.c

## Purpose
`coresight-cti-platform.c` parses firmware data for CTI devices and builds the trigger-connection metadata consumed by the CTI core and sysfs layers.

## Important APIs, Types, And Functions
The file defines DT property names such as `trig-conns`, `arm,cs-dev-assoc`, trigger signal/type arrays, filters, connection names, and CTM ID. `cti_plat_get_cpu_at_node()` resolves CPU affinity. `cti_plat_get_node_name()` and `cti_plat_get_csdev_or_node_name()` produce association names and optional `coresight_device` pointers. `cti_plat_create_v8_connections()` builds architecturally-defined PE and optional ETM connections. `cti_plat_create_connection()` parses implementation-defined child connection nodes. `coresight_cti_get_platform_data()` returns a minimal CoreSight platform-data object after populating CTI-specific metadata in `drvdata`.

## Control Flow
During CTI probe, `coresight_cti_get_platform_data()` allocates zeroed platform data and calls `cti_plat_get_hw_data()`. That reads `arm,cti-ctm-id`, chooses v8 architectural parsing if compatible, otherwise walks child nodes named `trig-conns`, and falls back to a default all-trigger connection if no explicit connections were found. Each parsed connection allocates input/output trigger groups, reads signal indexes and optional signal types, applies filter signals, resolves CPU or CoreSight device association, and appends the connection to `drvdata->ctidev.trig_cons`.

## State And Persistence
The parser mutates `drvdata->ctidev` and `drvdata->config`: CPU affinity, CTM ID, trigger connection list, trigger-use masks, and output filters. The returned `coresight_platform_data` is intentionally mostly empty because CTI does not use normal trace-path input/output topology for data flow.

## Dependencies And Integration Points
The file depends on generic firmware property APIs, OF helpers, DT binding constants in `dt-bindings/arm/coresight-cti-dt.h`, and CTI core allocation/connection APIs. It integrates firmware declarations with CTI sysfs dynamic groups and association fixup in the core.

## Risks
Signal count and type arrays must agree with hardware `nr_trig_max`; inconsistent firmware returns `-EINVAL`. `cti_plat_read_trig_group()` builds masks from supplied signal indexes but does not explicitly check each index against `nr_trig_max` in that function, relying on count checks and later usage. Association by node name is fragile when device registration ordering or firmware naming differs. The v8 architectural defaults hard-code signal masks and types, so binding compatibility must be accurate.

## Test Signals
DT parsing tests should cover v8 architectural CTIs with CPU and ETM association, implementation-defined connections with signal/type/filter arrays, missing CPU errors, fallback default connections, invalid oversized arrays, and association when referenced CoreSight devices register before or after the CTI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-sysfs.c

## Purpose
`coresight-cti-sysfs.c` exposes CTI state and controls through static and dynamically generated sysfs attribute groups. It lets users enable CTIs, inspect management/programming registers, program trigger-to-channel routing, gate channels, emit software channel events, configure output filtering, and inspect firmware-described trigger connections.

## Important APIs, Types, And Functions
Static attributes include `enable`, `powered`, `ctmid`, and `nr_trigger_cons`. Management/register attributes use `coresight_cti_reg*()` helpers. Cached programming helpers `cti_reg32_show()` and `cti_reg32_store()` read active hardware or cached state and write through when active. Channel operations are parsed by `cti_trig_op_parse()` and `chan_op_parse()` and call core APIs such as `cti_channel_trig_op()`, `cti_channel_gate_op()`, and `cti_channel_setop()`.

Dynamic connection sysfs is built by `cti_create_cons_sysfs()`, `cti_create_con_attr_set()`, and `cti_create_con_sysfs_attr()`. Each connection gets a `triggers<N>` group with `name`, signal masks, and signal type names as applicable.

## Control Flow
At CTI probe, after platform parsing has populated the connection list, `cti_create_cons_sysfs()` allocates the combined group pointer table, installs static group pointers, then walks each `cti_trig_con` to create a dynamic `triggers<N>` group. During normal operation, sysfs writes parse user input, validate indexes or bitmasks through CTI core helpers, update cached config under the CTI spinlock, and write hardware only if the CTI is currently active. `enable_store()` handles runtime PM and calls CTI enable/disable helper paths.

## State And Persistence
Most sysfs programming updates `drvdata->config`, which persists while the device exists and is replayed by `cti_write_all_hw_regs()` on enable. Dynamic attributes store a pointer to the relevant `cti_trig_con` in `dev_ext_attribute.var`. `ctiinout_sel` and `xtrig_rchan_sel` are selector state used by several show/store attributes.

## Dependencies And Integration Points
The file depends on CTI core APIs, runtime PM, CoreSight register offsets, sysfs helpers, and platform-populated connection metadata. The exported `coresight_cti_groups` array is consumed by CTI core registration as the device's sysfs groups.

## Risks
Sysfs inputs directly affect cross-trigger routing; validation must prevent out-of-range channels/triggers and filtered output triggers unless filtering is intentionally disabled. Some show paths use `sprintf()` into sysfs buffers, though outputs are small. `pm_runtime_get_sync()` return handling in register reads does not check negative errors before register access. Dynamic attributes rely on devm lifetime and correct group-array sizing.

## Test Signals
Tests should inspect all static groups, dynamic `triggers<N>` groups for varied connection shapes, enable/disable runtime PM behavior, register visibility when ASICCTL is absent, attach/detach validation, filter enforcement, channel list rendering, reset behavior while active/inactive, and lockdep under concurrent sysfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti.h

## Purpose
`coresight-cti.h` defines CTI register offsets, trigger/connection/configuration structures, operation enums, and internal function prototypes shared by the CTI core, platform parser, and sysfs implementation.

## Important APIs, Types, And Functions
Register definitions cover CTI control, interrupt acknowledge, app set/clear/pulse, input/output enable arrays, trigger/channel status, gate, ASIC control, integration-test registers, and management affinity registers. `struct cti_trig_grp` describes a group of related trigger signals with a used-mask and per-signal type IDs. `struct cti_trig_con` connects a CTI to a CPU/CoreSight/other device and carries dynamic sysfs metadata.

`struct cti_device` stores CTI topology metadata: connection count, CTM ID, trigger connection list, CPU affinity, and sysfs group table. `struct cti_config` caches hardware programming and capability state. `struct cti_drvdata` is the top-level device state. Enums describe channel attach/detach, trigger direction, gate operations, and software channel set/clear/pulse operations. Prototypes expose CTI core/platform/sysfs functions within the CTI driver.

## Control Flow
The header has no direct control flow, but it defines the shared contract: platform parsing fills `cti_device`/connection data, sysfs mutates `cti_config`, and core enable writes the cached config to hardware.

## State And Persistence
The persistent runtime state is the combination of `cti_device` and `cti_config` inside `cti_drvdata`. Cached CTIINEN/CTIOUTEN, gate, app-set, ASIC control, filters, and selectors persist while the driver is bound and are replayed on enable.

## Dependencies And Integration Points
The header depends on CoreSight public/private headers, sysfs, lists, spinlocks, and kernel types. It is private to the CTI implementation family but central to all three CTI C files.

## Risks
`CTIINOUTEN_MAX` bounds arrays at 32; hardware values are clamped in core but all users must respect `nr_trig_max`. Flexible allocation of `cti_trig_grp.sig_types[]` requires exact sizes. Dynamic sysfs pointers in `cti_trig_con` must remain valid for the device lifetime.

## Test Signals
Compile coverage across CTI core/platform/sysfs is essential. Runtime tests should verify capability limits, flexible trigger group allocation, connection list lifetime, and cached config replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-dummy.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-dummy.c

## Purpose
`coresight-dummy.c` provides lightweight CoreSight dummy source and sink devices for topologies where a real endpoint is absent or where a placeholder is needed for testing and graph completion.

## Important APIs, Types, And Functions
`struct dummy_drvdata` stores the parent device, registered CoreSight device, and optional trace ID for dummy sources. Source callbacks are `dummy_source_enable()`, `dummy_source_disable()`, and `dummy_source_trace_id()`. Sink callbacks are `dummy_sink_enable()` and `dummy_sink_disable()`. A read-only `traceid` sysfs attribute is exposed for dummy sources.

## Control Flow
Probe distinguishes `arm,coresight-dummy-source` from `arm,coresight-dummy-sink`. For a source, it allocates a CoreSight source name, sets source subtype `OTHERS`, installs source ops, and obtains either a static trace ID from device tree or a dynamic system trace ID. For a sink, it allocates a sink name and registers subtype `DUMMY`. Both paths load CoreSight platform data, register the device, and enable runtime PM. Remove releases any valid trace ID, disables runtime PM, and unregisters the CoreSight device.

Enable for a dummy source uses `coresight_take_mode()` to prevent conflicting modes and otherwise only logs; disable sets mode back to disabled. Dummy sink operations log and return success without hardware programming.

## State And Persistence
The only meaningful persistent state is the source trace ID and CoreSight mode. There is no hardware buffer or register state. The trace ID is held for the lifetime of a dummy source and returned to the trace ID allocator on remove.

## Dependencies And Integration Points
The driver depends on OF compatible strings, CoreSight platform data, CoreSight registration, trace ID allocation, and runtime PM. It integrates with normal CoreSight path construction as either a source or sink.

## Risks
Dummy devices can make a topology appear valid while no real trace capture or generation occurs. Static trace ID conflicts are delegated to the trace ID allocator; failures abort probe. Source ops do not include perf-specific behavior beyond mode ownership, so tests should not treat dummy trace as real data.

## Test Signals
Tests should cover source and sink probe, static and dynamic trace ID allocation, trace ID sysfs read, mode conflict on enable, remove-time ID release, and path construction through dummy endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etb10.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etb10.c

## Purpose
`coresight-etb10.c` implements the CoreSight Embedded Trace Buffer v1.0 sink. It can capture trace into on-chip RAM, expose captured data through a misc character device for sysfs-style sessions, and integrate with perf AUX buffers for perf sessions.

## Important APIs, Types, And Functions
`struct etb_drvdata` stores MMIO base, optional AT clock, CoreSight device, misc device, spinlock, single-reader flag, active PID, software dump buffer, hardware depth, and trigger counter. Hardware control is split into `__etb_enable_hw()`, `etb_enable_hw()`, `__etb_disable_hw()`, `etb_dump_hw()`, and `etb_disable_hw()`. CoreSight sink callbacks are `etb_enable()`, `etb_disable()`, `etb_alloc_buffer()`, `etb_free_buffer()`, and `etb_update_buffer()`.

User-space misc-device functions are `etb_open()`, `etb_read()`, and `etb_release()`. Sysfs exposes `trigger_cntr` and a `mgmt` register group. Probe registers the ETB as a CoreSight sink subtype `SINK_BUFFER`.

## Control Flow
Probe maps the AMBA resource, enables the AT clock, reads hardware buffer depth, allocates a software copy buffer, loads CoreSight platform data, clears stale claim tags, registers the CoreSight sink, and registers a misc device named after the CoreSight device. Sysfs enable rejects perf-owned sessions, claims hardware, clears RAM, programs trigger/formatter registers, enables capture, and sets mode. Perf enable rejects sysfs ownership, pins the monitored PID, sets up the perf buffer position, enables hardware, and increments refcounts.

Disable decrements `csdev->refcnt`; only the final disable flushes and stops the formatter, dumps ETB RAM into the software buffer, disclaims hardware, resets PID, and disables mode. Perf update stops capture, computes the readable region from RAM pointers and status, handles wrap/loss with barrier packets and `PERF_AUX_FLAG_TRUNCATED`, copies words into the AUX ring, resets RAM pointers, and re-enables capture.

## State And Persistence
Hardware state includes ETB RAM, read/write pointers, trigger counter, formatter control/status, and capture enable. Software state includes `drvdata->buf` for sysfs reads, `pid` ownership for perf, `local_t reading` for single misc-reader exclusion, `trigger_cntr`, and CoreSight mode/refcount.

## Dependencies And Integration Points
The driver depends on AMBA, CoreSight sink ops, ETM perf AUX buffer helpers, runtime PM, miscdevice, copy_to_user, circular buffer macros, claim tags, and the common CoreSight barrier packet. It integrates as a selectable default or explicit sink in CoreSight paths.

## Risks
Buffer pointer arithmetic is in ETB words in some paths and bytes in others; frame-size alignment handling is critical for decoders. Perf snapshot and non-snapshot modes intentionally differ in truncation behavior. `csdev->refcnt != 1` in update avoids stealing from shared sessions but can skip data. The misc-device lifetime comment relies on fops references after deregistration. Trigger counter store parses hex only.

## Test Signals
Tests should cover probe depth validation, sysfs capture/read, single-reader exclusion, perf allocation/update in snapshot and non-snapshot modes, wrap/full buffer handling, barrier insertion, formatter timeout logging, runtime PM, mode conflicts, and removal while the misc device has open file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etb10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-cp14.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-cp14.c

## Purpose
`coresight-etm-cp14.c` provides ETM register read/write access through ARM CP14 coprocessor instructions for ETM implementations accessed via CP14 rather than MMIO.

## Important APIs, Types, And Functions
The file exports `etm_readl_cp14(u32 reg, unsigned int *val)` and `etm_writel_cp14(u32 reg, u32 val)`. Both are large switch statements mapping logical ETM register offsets/macros from `coresight-etm.h` to architecture-specific `etm_read()` and `etm_write()` CP14 register identifiers from `asm/hardware/cp14.h`.

Read coverage includes control, configuration, trigger, status, trace enable, FIFO, address comparators, access type registers, counters, sequencer events, external outputs, context ID comparators, implementation-specific registers, sync, ID, external input selection, timestamp, aux, trace ID, VMID, OS lock/status, and powerdown registers. Write coverage is similar but limited to writable registers and returns `-EINVAL` for unsupported offsets.

## Control Flow
Callers pass a logical ETM register offset. The switch selects the corresponding CP14 register access and returns 0 on success. Unknown offsets set read output to 0 and return `-EINVAL`, or return `-EINVAL` for writes without touching hardware.

## State And Persistence
There is no software state in this file. All state is in the ETM hardware registers reached by CP14 accesses. Writes persist according to ETM hardware and CPU debug power behavior.

## Dependencies And Integration Points
The file depends on ARM CP14 accessors and ETM register macro definitions. It is an access backend used by ETM driver code that abstracts register I/O across MMIO and CP14 implementations.

## Risks
The switch tables must stay synchronized with ETM register definitions and CP14 architectural register names. Missing writable cases can make higher-level ETM programming fail with `-EINVAL`; incorrectly writable cases can write read-only or unsafe registers. CP14 access is architecture-specific and generally relevant to older ARM/ETM designs.

## Test Signals
Compile tests on supported ARM configurations are the first signal. Runtime tests should read known ID/config registers through CP14, write/read back safe programmable registers, and verify unsupported offsets return `-EINVAL` without side effects. Higher-level ETM enable tests indirectly validate the mapping completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-cp14.c -->
