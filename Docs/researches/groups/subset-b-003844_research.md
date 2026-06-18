# Research: subset-b-003844

Grouped research for CoreSight files under `sources/distributed-fs/ceph-client/drivers/hwtracing/coresight`. Each section preserves the source path in its title and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x.h

## Purpose
This header is the main ETMv4/ETE register and data-contract definition file for CoreSight instruction trace sources. It defines trace register offsets, field masks, sysreg access tables, MMIO/sysreg read/write wrappers, supported resource limits, mode bits, architecture identity helpers, and the driver-private configuration/save-state structures used by the ETM4 driver implementation.

## Important APIs, Types, And Functions
Important macros include `TRC*` register offsets, `TRCIDR*` capability masks, `TRCCONFIGR_*`, `TRCVICTLR_*`, address-comparator masks, resource selector helpers, and ETM mode bits such as `ETMv4_MODE_TIMESTAMP`, `ETM_MODE_EXCL_KERN`, and `ETM_MODE_EXCL_USER`. `etm4_res_sel_single()` and `etm4_res_sel_pair()` validate and encode event resource selectors, warning on invalid selector widths and rejecting pair selector zero. The `ETM_COMMON_SYSREG_LIST`, `ETM4x_ONLY_SYSREG_LIST`, `ETE_ONLY_SYSREG_LIST`, and `ETM_MMAP_LIST` macro lists are central to selecting whether an offset may be accessed through system registers or only through MMIO. `etm4x_relaxed_read32/64`, `etm4x_read32/64`, and matching write macros abstract over `struct csdev_access` choosing `base` MMIO when `io_mem` is true or `etm4x_sysreg_read/write()` otherwise. The main types are `struct etmv4_config`, `struct etmv4_save_state`, and `struct etmv4_drvdata`.

## Control Flow And State
This file is declarative, but it drives runtime control flow in the ETM driver. Probe code fills `struct etmv4_drvdata` from hardware ID registers, user/syscfg/perf selection mutates `struct etmv4_config`, hardware enable programs the register fields from that config, and CPU power loss or low-power handling uses `struct etmv4_save_state` to preserve trace registers. Access wrappers insert architecture barriers around non-relaxed operations, which matters for ordering trace register programming around enable and disable.

## Dependencies And Integration Points
The header depends on `coresight-priv.h`, `asm/sysreg.h`, bitfield helpers, raw spinlocks, and CoreSight framework types. It integrates with the ETM sysfs groups through `coresight_etmv4_groups`, with trace-id lifecycle through `etm4_release_trace_id()`, and with architecture-specific system-register access through `etm4x_sysreg_read()` and `etm4x_sysreg_write()`.

## Risks And Test Signals
The highest-risk area is drift between architected register accessibility and the sysreg/MMIO case lists. A missing register in the sysreg switch can make valid sysreg-only hardware inaccessible; placing MMIO-only registers in sysreg paths can fault or read undefined values. Save-state coverage must track any register programmed during enable, or suspend/resume can silently lose trace configuration. Useful tests are build coverage on arm64, ETMv4 and ETE probe on sysreg and MMIO implementations, sysfs reads of management registers, low-power resume trace validation, and perf trace sessions that exercise trace IDs, filters, address comparators, and syscfg-selected features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-funnel.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-funnel.c

## Purpose
This file implements the CoreSight funnel link driver. A funnel merges multiple input trace streams into one output stream. The driver supports static platform-described funnels and dynamic AMBA funnels with programmable registers.

## Important APIs, Types, And Functions
`struct funnel_drvdata` stores MMIO base, optional `atclk` and `pclk`, the registered `coresight_device`, port priority, and a raw spinlock. `funnel_enable()` and `funnel_disable()` implement `coresight_ops_link` and manage `in->dest_refcnt` so the same input port can be shared by nested paths. Dynamic hardware operations are handled by `dynamic_funnel_enable_hw()` and `dynamic_funnel_disable_hw()`, which unlock CoreSight management registers, claim/disclaim the device, set hold time, toggle the selected input bit in `FUNNEL_FUNCTL`, and write `FUNNEL_PRICTL`. Sysfs attributes expose `priority` and read-only `funnel_ctrl`.

## Control Flow And State
Probe flows through `funnel_platform_probe()` or `dynamic_funnel_probe()` into common `funnel_probe()`. The common path allocates a unique CoreSight name, enables clocks, maps MMIO when a resource is present, gets firmware topology with `coresight_get_platform_data()`, and registers a `CORESIGHT_DEV_TYPE_LINK` with subtype `CORESIGHT_DEV_SUBTYPE_LINK_MERG`. Enable/disable is serialized by `drvdata->spinlock`; hardware programming occurs only on the first enable or last disable for a port.

## Dependencies And Integration Points
The driver uses platform and AMBA registration through `coresight_init_driver()`, runtime PM clock callbacks, firmware matching for OF and ACPI, and common CoreSight claim/lock helpers from `coresight-priv.h`. It depends on connection state maintained by the CoreSight path builder through `struct coresight_connection`.

## Risks And Test Signals
Refcount underflow on disable would incorrectly clear an active port, so path construction and balanced enable/disable are important. `priority_store()` accepts any hex value and does not mask to implemented fields, so invalid priority values rely on hardware tolerance. Dynamic funnels without MMIO behave as static links and skip register programming. Test signals include OF/ACPI probe, sysfs `funnel_ctrl` reads under runtime PM, multiple simultaneous paths sharing an input, claim failure handling on first enable, and suspend/resume clock sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-funnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-kunit-tests.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-kunit-tests.c

## Purpose
This is a small KUnit test file for CoreSight framework behavior. It currently verifies default sink discovery across a simple source-to-helper topology.

## Important APIs, Types, And Functions
`coresight_test_device()` allocates a minimal `struct coresight_device` and `struct coresight_platform_data` from a KUnit device. `test_default_sink()` creates four synthetic devices: a bus source, an ETF linksink buffer, an ETR sysmem sink, and a CATU helper. It connects them with `coresight_add_out_conn()` and asserts that `coresight_find_default_sink(src)` returns the ETR rather than the intermediate ETF or helper.

## Control Flow And State
The test registers a KUnit device, constructs fake CoreSight devices in memory, assigns enough type/subtype metadata for sink search, and creates output connections in source order. No hardware is touched, no runtime PM is involved, and all allocations are device-managed under KUnit lifetime. The expected search flow is source to ETF to ETR, with the helper hanging off ETR but not changing the sink choice.

## Dependencies And Integration Points
The test includes `linux/coresight.h` and `coresight-priv.h`, and exercises exported framework connection and sink-selection helpers. It is registered via `kunit_test_suites()` under suite name `coresight_test_suite`.

## Risks And Test Signals
Coverage is intentionally narrow. It does not verify cycles, multiple sinks, per-CPU TRBE preference, disabled devices, missing `pdata`, or failure allocation paths. Its value is as a regression signal for default sink semantics, especially ensuring helper devices do not become selected sinks and that intermediate link-sinks do not mask a downstream sysmem sink when the source subtype is not `SOURCE_PROC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-kunit-tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-platform.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-platform.c

## Purpose
This file parses firmware topology data for CoreSight devices and converts it into `coresight_platform_data` connection arrays. It supports Device Tree graph bindings, legacy DT bindings, and ACPI _DSD graph bindings, and provides CPU/static trace-id helpers.

## Important APIs, Types, And Functions
`coresight_add_out_conn()` appends a new output connection to a device, rejecting duplicate output ports except helper-style `src_port == -1`. `coresight_add_in_conn()` stores a reverse input reference on the destination device. `coresight_find_csdev_by_fwnode()` locates registered CoreSight devices by firmware node. OF parsing is centered on `of_coresight_parse_endpoint()` and `of_get_coresight_platform_data()`. ACPI parsing is centered on `_DSD` graph validation, `acpi_coresight_parse_link()`, and `acpi_coresight_parse_graph()`. Public helpers include `coresight_get_cpu()`, `coresight_get_static_trace_id()`, and `coresight_get_platform_data()`.

## Control Flow And State
For each output endpoint or ACPI master link, the parser resolves the remote endpoint/device, defers probing when the remote device is not yet present, stores a referenced destination fwnode, records source and destination port numbers, and optionally resolves a `filter-source` reference to a source device. Parsed connections are devm-managed under the local device and later completed by CoreSight registration/matching. ACPI input links are parsed only for direction validation and local input port awareness; output links produce actual `out_conns`.

## Dependencies And Integration Points
The file depends on OF graph APIs, ACPI object parsing, platform and AMBA bus lookup, `coresight-priv.h`, and `linux/coresight.h`. It is used by nearly every CoreSight component probe before `coresight_register()`. Remote fwnode references are released by platform-data cleanup outside this file.

## Risks And Test Signals
Topology parsing is probe-order sensitive; missing remote devices return `-EPROBE_DEFER`, while malformed graph data can abort a device probe. Duplicate output ports are rejected early. Reference ownership is subtle because destination fwnodes and bus devices are acquired during parsing and must be released on failure/unregister. Test signals include OF new and legacy bindings, ACPI graph packages with valid and invalid directions, disabled remote nodes, filter-source validation, duplicate ports, CPU phandle or ACPI parent CPU mapping, and static trace-id property reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-priv.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-priv.h

## Purpose
This private header collects shared internal CoreSight definitions used across framework and component drivers. It defines management register offsets, claim protocol values, sysfs helper attribute containers, shared buffer structures, lock/unlock helpers, path management prototypes, AMBA ID macros, and syscfg/per-CPU sink helper declarations.

## Important APIs, Types, And Functions
Core definitions include `CORESIGHT_ITCTRL`, `CORESIGHT_CLAIMSET`, `CORESIGHT_LAR`, `CORESIGHT_DEVARCH`, and claim state constants. `struct cs_pair_attribute` and `struct cs_off_attribute` back generic management-register sysfs attributes generated by `coresight_simple_reg32()` and `coresight_simple_reg64()`. `struct cs_buffers` describes perf AUX buffer state for sinks. `CS_UNLOCK()` writes `CORESIGHT_UNLOCK` to LAR and uses memory barriers; `CS_LOCK()` writes zero to LAR after a barrier. AMBA helper macros include `CS_AMBA_ID`, `CS_AMBA_ID_DATA`, `CS_AMBA_UCI_ID`, and `CS_AMBA_MATCH_ALL_UCI`.

## Control Flow And State
This header does not own runtime state, but it defines the contracts that component drivers use to mutate shared CoreSight path and device state. Path functions declared here build, enable, disable, release, and assign trace IDs. The claim protocol constants coordinate self-hosted and external debugger ownership. `cs_buffers` persists per-perf-session cursor, page, offset, snapshot, and size accounting.

## Dependencies And Integration Points
It depends on AMBA, IO accessors, CoreSight public headers, PM runtime, and bit operations. It is included by almost all files in this subset, making it the integration point for sysfs links, CTI association hooks, ETM CP14 fallback stubs, syscfg registration, source pause/resume, and per-CPU sink state.

## Risks And Test Signals
Because this is a private cross-driver contract, small changes can have wide blast radius. Lock/unlock ordering must remain compatible with hardware management registers. The `coresight_simple_reg*` compound-literal attribute macros depend on static storage semantics in initializer contexts and should not be repurposed casually. Test signals are broad build coverage across configs with and without ETM3X, sysfs management-register reads for multiple device classes, AMBA ID matching with UCI data, and path enable/disable tests that exercise claim, CTI, and trace-id functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-replicator.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-replicator.c

## Purpose
This file implements the CoreSight replicator link driver. A replicator splits one incoming trace stream to one or two outgoing trace paths. The driver supports static replicators and programmable dynamic replicators.

## Important APIs, Types, And Functions
`struct replicator_drvdata` stores MMIO base, clocks, the CoreSight device, a raw spinlock, and `check_idfilter_val` for hardware that loses filter context when clocks are removed. `dynamic_replicator_enable()` clears `REPLICATOR_IDFILTER0` or `REPLICATOR_IDFILTER1` to enable an output port, claiming the device when both filters were disabled. `dynamic_replicator_disable()` writes `0xff` to the selected filter and disclaims when both outputs are disabled. `replicator_enable()` and `replicator_disable()` wrap those operations in CoreSight link refcounting using `out->src_refcnt`. Sysfs management attributes expose `idfilter0` and `idfilter1`.

## Control Flow And State
Probe enters through platform or AMBA paths and shares `replicator_probe()`. It allocates a unique name, enables clocks, maps MMIO if present, reads firmware topology, initializes the spinlock, registers a `CORESIGHT_DEV_TYPE_LINK` with split subtype, and resets programmable hardware to both outputs disabled. The Qualcomm context-loss property makes enable treat both zero filters as equivalent to reset-disabled `0xff`.

## Dependencies And Integration Points
The driver uses CoreSight claim helpers, runtime PM clocks, AMBA IDs, OF/ACPI matches, `coresight_get_platform_data()`, and `coresight_init_driver()`. It is a path-builder link device, so its correctness depends on `struct coresight_connection` source-port refcounts.

## Risks And Test Signals
Only output ports 0 and 1 are supported; invalid ports trigger `WARN_ON()` and `-EINVAL` or return. Context-loss recovery is hardware-specific and depends on firmware declaring `qcom,replicator-loses-context`. Refcount imbalance can leave a filter open or prematurely disclaim the component. Test signals include dynamic and static probe, sysfs reads of ID filters, dual-output tracing, repeated enable/disable on the same outport, context-loss after runtime suspend, and claim failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-replicator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-self-hosted-trace.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-self-hosted-trace.h

## Purpose
This small arm64 helper header wraps access to the self-hosted trace filter control register `TRFCR_EL1`. It is used by trace source code that needs to enable or restore architectural tracing controls outside CoreSight MMIO blocks.

## Important APIs, Types, And Functions
`read_trfcr()` returns `read_sysreg_s(SYS_TRFCR_EL1)`. `write_trfcr(u64 val)` writes `SYS_TRFCR_EL1` and immediately executes `isb()` so subsequent execution observes the new trace filter state.

## Control Flow And State
The header owns no storage. It provides ordered register access for callers that store desired TRFCR values in their own driver state, such as ETM/ETE code maintaining per-CPU trace enable state.

## Dependencies And Integration Points
The only direct dependency is `asm/sysreg.h`. Integration is architecture-specific: this helper is meaningful on arm64 CPUs implementing self-hosted trace controls and is expected to be included only in code paths where `SYS_TRFCR_EL1` is valid.

## Risks And Test Signals
The main risk is calling it on unsupported architecture/configuration paths or forgetting the synchronization requirement after writes. The `isb()` in `write_trfcr()` is the critical ordering behavior. Test signals are compile coverage for arm64 trace builds and runtime ETM/ETE sessions that require TRFCR programming across enable, disable, CPU hotplug, and power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-self-hosted-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-stm.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-stm.c

## Purpose
This file implements the CoreSight System Trace Macrocell driver. STM is a software and hardware event trace source that exposes stimulus ports through the generic Linux STM framework and registers as a CoreSight source.

## Important APIs, Types, And Functions
`struct stm_drvdata` stores programming MMIO, stimulus channel space, clocks, CoreSight and generic STM objects, trace ID, port/event register caches, channel count, write granularity, and the guaranteed-channel bitmap. CoreSight source operations are `stm_enable()`, `stm_disable()`, and `stm_trace_id()`. Generic STM integration uses `stm_generic_packet()`, `stm_mmio_addr()`, `stm_generic_link()`, `stm_generic_unlink()`, and `stm_generic_set_options()`. Sysfs attributes expose hardware event enable/select, port enable/select, and trace ID. Probe is handled by `__stm_probe()` for AMBA and platform devices.

## Control Flow And State
Probe maps the programming resource and the separate stimulus resource, determines 32-bit versus 64-bit writes from `STMSPFEAT2R`, determines stimulus port count from boot parameter or `CORESIGHT_DEVID`, allocates the guaranteed bitmap, registers with the generic STM subsystem, gets CoreSight platform data, registers as a software source, and allocates a system trace ID. `stm_enable()` only accepts sysfs mode, takes CoreSight mode ownership, powers the device, and programs event tracing, stimulus ports, synchronization, timestamping, and global enable. Packet writes verify the source is enabled, validate channel number, derive packet address from packet type and options, clamp size to supported write width, and perform aligned writes.

## Dependencies And Integration Points
The driver depends on AMBA/platform buses, runtime PM, generic STM APIs, CoreSight trace-id allocation, firmware stimulus-area description, and `coresight_enable_sysfs()`/`coresight_disable_sysfs()` for generic STM link/unlink. It integrates with perf only indirectly through CoreSight path mode checks; direct enable rejects non-sysfs modes.

## Risks And Test Signals
Stimulus mapping is firmware-sensitive: DT requires `stm-stimulus-base`, while ACPI expects the second memory resource. Packet writes are marked `notrace` and must avoid recursion or sleeping. Channel option changes are rejected unless tracing is enabled, and out-of-range channels fail. Trace ID acquisition failure unwinds CoreSight and STM registration. Test signals include generic STM character/device writes, sysfs enable/disable, channel guaranteed/invariant options, 32-bit and 64-bit packet writes, boot `boot_nr_channel`, OF/ACPI resource parsing, and runtime PM clock failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-stm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.c

## Purpose
This file projects the CoreSight system configuration manager into configfs. It creates a `cs-syscfg` subsystem with `configurations` and `features` groups, exposes loaded configuration descriptors, presets, feature metadata, and mutable feature parameters, and forwards activation/parameter changes to the syscfg core.

## Important APIs, Types, And Functions
Configuration attributes include read-only `description`, read-only `feature_refs`, read/write `enable`, and read/write `preset`. Preset groups expose `values`. Feature attributes include `description`, `matches`, and `nr_params`. Per-parameter groups expose a `value` attribute. Public entry points are `cscfg_configfs_init()`, `cscfg_configfs_release()`, `cscfg_configfs_add_config()`, `cscfg_configfs_add_feature()`, `cscfg_configfs_del_config()`, and `cscfg_configfs_del_feature()`.

## Control Flow And State
Initialization allocates a config item type from `cscfg_device()`, names the subsystem `cs-syscfg`, initializes default `configurations` and `features` groups, and registers the subsystem. Adding a config allocates a `cscfg_fs_config`, initializes its config group, creates default `presetN` groups, registers it under `configurations`, and stores the group pointer in the descriptor. Enabling a config parses a boolean, calls `cscfg_config_sysfs_activate()`, records local active state, and updates the sysfs preset if enabling. Parameter writes parse `u64` and call `cscfg_update_feat_param_val()`.

## Dependencies And Integration Points
This file depends on configfs, descriptor types from `coresight-config.h`, wrappers from `coresight-syscfg-configfs.h`, and syscfg core APIs for activation, preset, feature lookup, and parameter update. Its allocations are devm-managed against the syscfg manager device.

## Risks And Test Signals
Configfs locking is intentionally separated from syscfg list locking by the core; changes here can reintroduce lock inversion. `cscfg_cfg_values_show()` assumes `cscfg_get_named_feat_desc()` succeeds for all feature refs, which relies on core validation and load ordering. Preset numbers are 1-based and must remain consistent with descriptor arrays. Test signals include mounting configfs, loading/unloading config sets, enabling one config and rejecting a second active sysfs config, invalid preset writes, parameter writes while active returning `-EBUSY`, and configfs removal on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.h

## Purpose
This header defines the configfs-facing wrapper objects and public configfs lifecycle functions for the CoreSight system configuration manager.

## Important APIs, Types, And Functions
`CSCFG_FS_SUBSYS_NAME` names the configfs subsystem `cs-syscfg`. `struct cscfg_fs_config` wraps a configuration descriptor, configfs group, active flag, and selected preset. `struct cscfg_fs_feature` wraps a feature descriptor and group. `struct cscfg_fs_param` identifies a parameter index within a feature descriptor. `struct cscfg_fs_preset` identifies a preset index within a configuration descriptor. Declared functions initialize/release configfs and add/delete config and feature groups.

## Control Flow And State
The wrapper state mirrors descriptor state into configfs item lifetimes. Config `active` and `preset` fields track the sysfs-control view exposed through configfs, while descriptor pointers remain owned by the syscfg core or the module that loaded them. Add/delete functions are called during syscfg load/unload sequences after descriptor list validation.

## Dependencies And Integration Points
The header depends on `linux/configfs.h` and `coresight-syscfg.h`. It is included by both the syscfg core and configfs implementation, forming the narrow interface between descriptor management and user-visible configfs objects.

## Risks And Test Signals
The structs embed `config_group`, so object lifetime must remain valid while configfs references exist. Descriptor ownership is external, making unload ordering important. Test signals include add/delete of configs and features with and without presets/parameters, active config toggles, and module unload while configfs entries are visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg-configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.c

## Purpose
This file implements the global CoreSight system configuration manager. It loads feature and configuration descriptors, attaches matching features/configs to registered CoreSight devices, exposes descriptors through perf and configfs, handles dynamic load/unload ordering, and manages activation counts for perf and sysfs-controlled trace sessions.

## Important APIs, Types, And Functions
Public APIs include `cscfg_load_config_sets()`, `cscfg_unload_config_sets()`, `cscfg_register_csdev()`, `cscfg_unregister_csdev()`, `cscfg_activate_config()`, `cscfg_deactivate_config()`, `cscfg_csdev_enable_active_config()`, `cscfg_csdev_disable_active_config()`, `cscfg_update_feat_param_val()`, `cscfg_config_sysfs_activate()`, and `cscfg_config_sysfs_get_active_cfg()`. Internally, `cscfg_load_feat_csdev()` creates per-device feature instances, `cscfg_add_csdev_cfg()` creates per-device config instances when features match, and `cscfg_owner_get/put()` pins module owners while active or while later loads depend on earlier ones.

## Control Flow And State
`cscfg_mgr` is a singleton protected by `cscfg_mutex`. It owns lists of registered devices, feature descriptors, config descriptors, load owners, global active count, configfs subsystem, sysfs active config hash/preset, and a load state. Loading is serialized by `load_state`: features load first, configs validate feature references, per-device instances are attached, perf symlinks are created, owner dependency is recorded, configfs entries are registered outside the mutex, and configs become available only at the end. Unload is allowed only when nothing is active and the owner is the last loaded. Activation increments descriptor and global counts and pins owners; per-device enable finds a matching active config, programs feature values with `cscfg_csdev_enable_config()`, and records `active_cscfg_ctxt`.

## Dependencies And Integration Points
This file depends on descriptor operations in `coresight-config.h`, perf integration in `coresight-etm-perf.h`, configfs helpers, module refcounting, CoreSight device feature/config lists, and device-managed allocation on each CoreSight component.

## Risks And Test Signals
The manager mixes mutex-protected global lists with per-device raw spinlocks. Ordering is critical around configfs operations, load/unload serialization, and active config enable racing with disable. Error unwinds must remove partially loaded descriptors, perf symlinks, configfs entries, and owner-list pins. Test signals include duplicate feature/config names, missing feature references, dynamic module load/unload in reverse order, unload rejection while active, parameter writes while active, sysfs single-active enforcement, perf multiple active configs, and device registration after descriptors are already loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.h

## Purpose
This header defines the internal and external API contract for the CoreSight system configuration manager. It declares the singleton manager state, registered-device entries, load-owner records, load-state enum, and functions used by CoreSight devices, configfs, perf, preload code, and dynamically loaded configuration modules.

## Important APIs, Types, And Functions
`enum cscfg_load_ops` distinguishes no operation, load, and unload. `struct cscfg_manager` stores the manager device, registered CoreSight devices, feature/config descriptor lists, load order, active count, configfs subsystem, sysfs active config/preset, and load state. `struct cscfg_registered_csdev` records a CoreSight device, match flags, feature-load ops, and list node. `struct cscfg_load_owner_info` records owner type and handle for dependency-aware unload. Function declarations cover initialization, preload, descriptor lookup/update, sysfs config activation, config-set load/unload, CoreSight device registration, active config enable/disable, and active sysfs config query.

## Control Flow And State
The header itself does not execute code, but the declared structures define syscfg persistence. Descriptor lists represent all loaded configuration material; `sys_active_cnt` prevents mutation while tracing uses any config; `load_order_list` enforces dependency-preserving reverse unload; and `sysfs_active_config/sysfs_active_preset` hold the single config selected for sysfs-controlled trace.

## Dependencies And Integration Points
It depends on configfs, CoreSight public device definitions, Linux device model, and `coresight-config.h` descriptor types. It is included by syscfg core, configfs support, and CoreSight source drivers that register feature support or enable active configs.

## Risks And Test Signals
Because this is an internal ABI among CoreSight modules, structure semantics must stay synchronized with `coresight-syscfg.c` and `coresight-syscfg-configfs.c`. Owner type handling must match module/preload lifecycle. Test signals are compile coverage for syscfg-enabled builds, module load/unload of config providers, and source-driver registration paths that call `cscfg_register_csdev()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-syscfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-sysfs.c

## Purpose
This file implements CoreSight sysfs controls and connection links. It allows users to mark sinks active, enable/disable sources through sysfs-created paths, expose labels and management-register attributes, and create bidirectional sysfs symlinks that describe topology.

## Important APIs, Types, And Functions
`coresight_simple_show_pair()` and `coresight_simple_show32()` read management registers under runtime PM and back the `coresight_simple_reg*` macros. `coresight_enable_sysfs()` validates a source, finds an activated sink, builds a path, assigns a trace ID, enables path and source, and stores the path either per CPU or in `path_idr`. `coresight_disable_sysfs()` reverses the operation, dropping source refcounts, retrieving the stored path, disabling, and releasing it. Sysfs attributes include `enable_sink`, `enable_source`, optional `label`, and `connections/nr_links`. Link helpers are `coresight_create_conns_sysfs_group()`, `coresight_add_sysfs_link()`, `coresight_make_links()`, and their removal counterparts.

## Control Flow And State
`coresight_mutex` serializes sysfs path state. Processor sources store one sysfs path per CPU in `tracer_path`; software, TPDM, and other sources store paths in `path_idr` keyed by a hash of the device name. Software sources may increment refcount when already enabled, supporting multiple applications. Sink selection recursively walks output connections until it finds `sysfs_sink_activated` on a sink or linksink.

## Dependencies And Integration Points
The file depends on CoreSight path operations, trace-id helpers, runtime PM, sysfs, IDR, firmware label properties, and device type registration. It exports helpers used by component drivers for management register groups and topology symlink creation.

## Risks And Test Signals
The path IDR uses a hashed device name as a fixed ID, so name collisions would break path lookup. Enable error unwinds must disable the path and release it in the right order. Source validation excludes unsupported source subtypes. Sysfs link removal decrements link counts and frees devm-allocated names. Test signals include sysfs path enable/disable for processor and software sources, multiple STM users, missing activated sink returning `-EINVAL`, perf/sysfs mode conflict, label visibility, link creation/removal, and management-register reads while runtime suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-core.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-core.c

## Purpose
This file implements common probe, userspace read, crashdata, sysfs attribute, and bus-registration logic for CoreSight Trace Memory Controller devices. It handles ETB, ETF, and ETR variants and delegates variant-specific trace capture to ETF/ETR helpers.

## Important APIs, Types, And Functions
Common hardware helpers are `tmc_wait_for_tmcready()`, `tmc_flush_and_stop()`, `tmc_enable_hw()`, `tmc_disable_hw()`, and `tmc_get_memwidth_mask()`. File operations `tmc_open()`, `tmc_read()`, and `tmc_release()` expose captured trace through a misc device. Crashdata operations expose reserved-memory trace from a previous boot. Probe logic in `__tmc_probe()` reads `CORESIGHT_DEVID`, determines config type and memory width, sets buffer size and ETR burst/capability data, maps reserved crash buffers, registers CoreSight device operations, and registers misc devices. Sysfs attributes expose trigger counter, buffer size, stop-on-flush, and management registers.

## Control Flow And State
For normal reads, open calls variant-specific read prepare, read copies trace slices to userspace, and release unprepares. Reserved crashdata validation checks buffer presence, metadata version, valid bit, trace physical address, metadata CRC, and trace-data CRC. If valid, metadata is converted into a readable circular-buffer view and a `crash_<name>` misc device is registered. Probe chooses ETB as sink buffer, ETF as link-sink FIFO, or ETR as sysmem sink based on hardware config bits.

## Dependencies And Integration Points
The file depends on AMBA/platform buses, reserved-memory OF helpers, DMA mask setup, miscdevice, runtime PM, `coresight-tmc.h`, ETF/ETR operation tables, CoreSight platform data, and CoreSight claim/access helpers. It integrates with ETR scatter-gather capability detection and SoC-600 UCI data.

## Risks And Test Signals
There is a notable risk in the `out:` path: crashdata validation is attempted even when earlier probe setup failed, so fields must be safe after partial initialization. Reserved-memory mappings can partially succeed, and crash metadata trust is guarded by version/address/CRC checks. Buffer-size writes are allowed only for ETR and require page alignment. Test signals include ETB/ETF/ETR probe, unsupported config rejection, misc read lifecycle, valid and invalid crash metadata, reserved-memory wraparound, ETR DMA mask selection, scatter-gather firmware properties, and runtime PM clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etf.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etf.c

## Purpose
This file implements ETB/ETF-specific Trace Memory Controller behavior. ETB acts as a sink backed by embedded SRAM; ETF can act as both sink and link FIFO. The file supports sysfs capture, perf AUX capture, panic crash synchronization, and misc-device read preparation.

## Important APIs, Types, And Functions
Hardware helpers include `__tmc_etb_enable_hw()`, `tmc_etb_enable_hw()`, `tmc_etb_dump_hw()`, `__tmc_etb_disable_hw()`, `tmc_etb_disable_hw()`, `__tmc_etf_enable_hw()`, `tmc_etf_enable_hw()`, and `tmc_etf_disable_hw()`. Sink operations are `tmc_enable_etf_sink()`, `tmc_disable_etf_sink()`, `tmc_alloc_etf_buffer()`, `tmc_free_etf_buffer()`, and `tmc_update_etf_buffer()`. Link operations are `tmc_enable_etf_link()` and `tmc_disable_etf_link()`. Read lifecycle functions are `tmc_read_prepare_etb()` and `tmc_read_unprepare_etb()`.

## Control Flow And State
Sysfs sink enable allocates or reuses `drvdata->buf`, rejects concurrent reading, enables ETB circular-buffer mode, sets CoreSight mode, and increments refcount. Perf enable rejects sysfs mode and concurrent readers, associates the sink with one PID, configures perf buffer cursor state, and enables hardware if this is the first user for that PID. Perf update flushes and stops hardware, computes unread bytes from RRP/RWP/full status, aligns truncation to memory width, copies TMC RAM words into perf AUX pages, optionally inserts a barrier packet when data was lost, and re-enables hardware if the event remains active. Link mode uses ETF hardware FIFO mode. Panic sync copies embedded SRAM to reserved trace memory and writes validated crash metadata.

## Dependencies And Integration Points
The file depends on `coresight-tmc.h`, perf AUX buffer support, `coresight-etm-perf.h`, common TMC helpers, CoreSight modes/refcounts, crash metadata helpers, and barrier packet helpers from `coresight-priv.h`.

## Risks And Test Signals
Concurrency is guarded by `drvdata->spinlock`, `drvdata->reading`, CoreSight mode, refcount, and PID association. Incorrect refcounting can leave hardware enabled or block reads. Perf truncation must respect TMC memory-width alignment or hardware read pointers can become invalid. Panic sync must avoid trusting invalid reserved buffers and must maintain metadata write ordering before setting `valid`. Test signals include sysfs capture/read/re-enable, perf snapshot and non-snapshot AUX capture, truncation flag behavior, multiple perf events for same and different PIDs, ETF link FIFO paths, concurrent read rejection, panic crashdata generation, and full-buffer barrier insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etf.c -->
