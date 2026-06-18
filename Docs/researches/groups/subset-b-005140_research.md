# Research Report: subset-b-005140

This grouped report covers the exact source files assigned to `subset-b-005140`. Each section preserves the source path in its title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-tpmi.c

Purpose: implements Intel TPMI-based Uncore Frequency Scaling (UFS) as an auxiliary driver bound to `intel_vsec.tpmi-uncore`. It exposes per-cluster and optional package-root uncore frequency controls through the shared `uncore-frequency-common` sysfs layer, replacing the older package-scoped MSR model with TPMI MMIO resources that can represent multiple power domains and fabric clusters per package.

Important APIs/types/functions: `struct tpmi_uncore_struct` owns package-wide state, power-domain array, root cluster, root min/max limits, and `write_blocked`; `struct tpmi_uncore_power_domain_info` tracks one TPMI resource and its cluster entries; `struct tpmi_uncore_cluster_info` embeds `struct uncore_data` consumed by the common uncore layer. `uncore_read()` and `uncore_write()` are registered via `uncore_freq_common_init()`. Helpers read/write CONTROL and STATUS qwords using bitfield masks for min/max/current ratios and efficiency latency control (ELC) fields. Probe uses `tpmi_get_feature_status()`, `tpmi_get_resource_count()`, `tpmi_get_resource_at_index()`, `tpmi_get_platform_data()`, and `tpmi_get_linux_die_id()`.

Control flow: `uncore_probe()` checks TPMI read/write blocking, initializes the common layer, allocates package state, gets OOBMSM platform mapping, maps each TPMI resource, validates UFS major/minor version, reads cluster masks and offsets, creates one sysfs entry per cluster, and optionally adds a root package entry when topology has one die and no partition. Reads dispatch min/max/current frequency, ELC fields, and Linux die id. Writes dispatch ELC or min/max frequency and enforce root-domain package-wide limits. Remove drops root and cluster sysfs entries and exits the common layer.

State/persistence: state is in devm allocations plus hardware CONTROL registers. Root-domain min/max writes are cached as ratio limits in `tpmi_uncore->max_ratio` / `min_ratio` and used to constrain later per-cluster writes. Hardware values persist according to firmware/MMIO behavior, not driver storage. `io_die_start[]`, `io_die_index_next`, and `domain_lock` provide static package-local IO domain numbering across probe-time cluster enumeration.

Dependencies/integration: depends on auxiliary bus, Intel VSEC, Intel TPMI, TPMI power-domain mapping, topology helpers, MMIO accessors, and the exported `INTEL_UNCORE_FREQUENCY` common namespace. It consumes feature devices produced by `vsec_tpmi.c` and exposes entries through the shared uncore sysfs ABI.

Risks: incorrect cluster offset/mask parsing can address wrong MMIO locations; root-domain writes apply to every cluster and can override per-cluster tuning; global IO-domain numbering assumes at most two partitions and careful ordering; ELC writes are silently unavailable on root domains, disabled autonomous UFS, older minor versions, or firmware write-blocked systems. Version and zero-mask checks are primary safety gates.

Test signals: probe on TPMI UFS hardware should create per-cluster uncore entries and optional root entry; invalid/blocked feature status should return `-ENODEV`; sysfs min/max/current frequency reads should reflect CONTROL/STATUS ratios multiplied by 100000 KHz; write tests should reject out-of-range ratios, root ELC writes, and write-blocked firmware; remove should leave no stale uncore entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c

Purpose: provides the older MSR-backed Intel uncore frequency limits driver. It exposes per-logical-die min/max/current frequency controls through the same common uncore sysfs layer used by the TPMI implementation, but operates on `MSR_UNCORE_RATIO_LIMIT` and `MSR_UNCORE_PERF_STATUS` through one online control CPU per die.

Important APIs/types/functions: global `uncore_instances` stores one `struct uncore_data` per logical die, `uncore_cpu_mask` records the selected control CPU for each die, and `uncore_hp_state` stores the dynamic CPU hotplug state. `uncore_read_control_freq()`, `uncore_write_control_freq()`, and `uncore_read_freq()` perform MSR access. `uncore_event_cpu_online()` and `uncore_event_cpu_offline()` manage sysfs entry lifetime and control CPU migration. `uncore_pm_notify()` restores stored limits after suspend/hibernate.

Control flow: module init rejects hypervisors, matches against a large Intel CPU model table, allocates die instances, initializes `uncore-frequency-common`, registers CPU hotplug callbacks, and registers a PM notifier. On CPU online, the first online CPU in a die creates/updates the uncore entry and becomes the control CPU. On offline, if the control CPU goes away, another CPU in the die is selected or the die sysfs entry is removed. Reads and writes run on `data->control_cpu`; writes update `stored_uncore_data` for resume restoration.

State/persistence: the live control state is hardware MSR state. The driver caches only the full ratio-limit MSR after successful writes so that PM resume can restore it. Entries are valid only while a control CPU exists for the die; `control_cpu < 0` produces `-ENXIO`.

Dependencies/integration: uses x86 CPU model matching, topology die/package helpers, CPU hotplug, suspend notifiers, MSR helpers, and the common uncore sysfs code in namespace `INTEL_UNCORE_FREQUENCY`.

Risks: hotplug races are mitigated by the common layer and CPUHP sequencing, but stale `control_cpu` values would break MSR access. `uncore_pm_notify()` returns early on the first invalid/empty entry, which can skip later entries. Writing raw ratio limits accepts any nonzero ratio up to the mask maximum and does not validate min <= max. The driver intentionally avoids virtualized environments.

Test signals: load on supported Intel bare metal should create die-scoped uncore entries as CPUs come online; CPU hotplug should migrate or remove entries; sysfs writes should change MSR 0x620 and survive suspend/resume when `stored_uncore_data` is set; unsupported CPUs and hypervisors should fail probe with `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c

Purpose: ACPI platform driver for Intel Virtual Button devices (`INT33D6`). It reports firmware button events and selected convertible/tablet switch events through input devices while avoiding known broken switch reporting on ordinary laptops.

Important APIs/types/functions: `struct intel_vbtn_priv` stores input devices, feature flags, mutex, dual-accelerometer detection result, and wakeup mode. `intel_vbtn_keymap` maps ACPI event scancodes to power, Windows, volume, and rotation keys. `intel_vbtn_switchmap` maps tablet-mode events and intentionally ignores dock events. `notify_handler()` processes ACPI notifications. `detect_tablet_mode()` evaluates `VGBS` and reports `SW_TABLET_MODE` / `SW_DOCK`. PM hooks manage wake events.

Control flow: probe checks `VBDL` for buttons and an allow-listed `VGBS` path for switches, allocates both input devices regardless of registration state, installs the ACPI notify handler, executes `VBDL` when buttons exist, samples tablet state, and enables device wake. Notifications are serialized by `priv->mutex`, looked up in sparse keymaps, lazily register the switches input device only for accepted systems, handle wakeup mode, and report autorelease events when no usable release scancode exists. Resume refreshes switch state.

State/persistence: runtime state is limited to registered input devices, booleans, and current wakeup mode. Switch state is read from ACPI `VGBS`; no persistent configuration is stored by the driver. `acpi_ec_mark_gpe_for_wake()` changes EC GPE wake marking at probe time.

Dependencies/integration: depends on ACPI, platform bus, Linux input/sparse-keymap, PM wakeup, DMI allow list, and `dual_accel_detect()` from platform/x86 helpers. It complements generic ACPI button handling by skipping button evdev reports during wake handling.

Risks: many firmware implementations misuse `SW_DOCK` and `VGBS`, so switch support is DMI-gated to avoid disabling keyboards/touchpads in userspace. Lazy switch device registration can fail during notify handling. Wakeup mode suppresses key reports by design and can look like missing input if misunderstood.

Test signals: ACPI notify scancodes should produce expected input events; allow-listed convertibles should expose tablet switch state and refresh it on resume; non-allow-listed laptops should not register switches; wake from power/volume events should call `pm_wakeup_hard_event()` without duplicate key reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c

Purpose: Intel PCIe Vendor Specific Extended Capability driver. It discovers Intel VSEC/DVSEC discovery tables on selected PCI devices, turns them into auxiliary devices for PMT telemetry/watcher/crashlog, SDSI, TPMI, and discovery features, and exports helper APIs for other code to register VSEC-backed auxiliary devices.

Important APIs/types/functions: `struct vsec_priv` tracks platform info, supplier devices, OOBMSM mapping, feature states, and found capability bitmap. `intel_vsec_add_aux()` creates an `intel_vsec_device` on the auxiliary bus. `intel_vsec_register()` registers static headers supplied by another device. `intel_vsec_register_device()`, `intel_vsec_walk_dvsec()`, and `intel_vsec_walk_vsec()` implement discovery. `intel_vsec_set_mapping()` and `intel_vsec_get_mapping()` store CPU-package-to-PCI mapping used by TPMI consumers. PCI error handlers tear down and rediscover auxiliary devices after reset.

Control flow: PCI probe enables the device, installs `vsec_priv`, then repeatedly scans DVSEC/VSEC/static headers until all expected capabilities are found or dependency skips are resolved. Each supported header is converted to resource ranges based on BAR base, table offset, entry count, and entry size, with memory-region availability checked before creating the auxiliary device. Dependency metadata delays consumers until supplier capabilities have been registered and device links can be created.

State/persistence: IDA allocators provide auxiliary IDs, `auxdev_array` tracks live devices for release and PCI error recovery, and `vsec_priv->state` records not found, registered, or skipped per feature. No persistent user state exists; hardware capability discovery is repeated on probe/reset.

Dependencies/integration: integrates PCI extended config access, auxiliary bus, xarray/IDA, device links, Intel VSEC public headers, and Kconfig presence checks for downstream feature drivers. Feature names such as `telemetry`, `sdsi`, `tpmi`, and `discovery` are consumed by auxiliary drivers.

Risks: feature dependency ordering is subtle; skipped suppliers can intentionally unblock consumers but missing configured drivers suppress auxiliary creation. Resource calculation depends on table offset quirks, entry size, and BAR selection. PCI error recovery removes all aux devices for the parent and reprobes, so consumers must tolerate teardown/recreation.

Test signals: supported PCI IDs should produce expected auxiliary devices only when corresponding downstream configs are enabled; dependency cases such as OOBMSM should create supplier links before telemetry consumers; invalid headers with zero entries/sizes or unsupported revisions should be skipped; AER slot reset should remove and recreate matching aux devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c

Purpose: auxiliary driver bound to `intel_vsec.tpmi` that enumerates TPMI PM Feature Structure entries and creates one auxiliary device per supported TPMI feature, such as RAPL, PEM, uncore, SST, and PLR. It also exposes TPMI control/status helpers and gated debugfs dumps.

Important APIs/types/functions: `struct intel_tpmi_pfs_entry` models hardware PFS entries; `struct intel_tpmi_pm_feature` stores one feature header and MMIO offset; `struct intel_tpmi_info` stores feature array, OOBMSM platform info, control MMIO, and debugfs directory. Exported APIs include `tpmi_get_platform_data()`, `tpmi_get_resource_count()`, `tpmi_get_resource_at_index()`, `tpmi_get_feature_status()`, `tpmi_register_notifier()`, `tpmi_unregister_notifier()`, and `tpmi_get_debugfs_dir()`. `tpmi_create_device()` constructs feature resources and calls `intel_vsec_add_aux()`.

Control flow: probe allocates `intel_tpmi_info`, reads each PFS header from resources provided by `vsec.c`, derives feature offsets from the PFS start plus capability offset in 1 KiB units, processes `TPMI_INFO_ID` to populate package/bus/device/function/partition/cdie mapping, maps the control feature when present, optionally creates debugfs, and creates feature auxiliary devices for enabled, named TPMI IDs. Feature status commands serialize through `tpmi_dev_lock`, negotiate TPMI control ownership, issue GET_STATE, wait for run-busy clear, copy response, and signal completion.

State/persistence: mapping and feature metadata live in devm-managed probe state. Hardware feature state is queried on demand through the TPMI control interface. Debugfs `mem_write` can mutate TPMI MMIO state and is exposed only when lockdown allows devmem and caller has `CAP_SYS_RAWIO`.

Dependencies/integration: depends on Intel VSEC aux devices, PCI parent data, MMIO/ioremap, debugfs, Linux security lockdown, capabilities, notifier chains, and Intel TPMI public headers. Downstream feature drivers bind to names like `intel_vsec.tpmi-uncore`.

Risks: PFS data is trusted hardware input but entry size is capped to 1 KiB for debug paths. `tpmi_get_feature_status()` assumes parent/driver data topology created by this driver. Control ownership timeouts or missing control memory cause feature-status failures. Debugfs write access is intentionally powerful and must remain gated.

Test signals: a TPMI VSEC device should produce per-feature auxiliary devices only for enabled supported TPMI IDs; `tpmi_get_resource_count()` and resource lookup should match PFS `num_entries`; feature-status reads should reflect read/write blocked bits; debugfs should appear only with raw IO permission and no devmem lockdown; remove should call TPMI core exit notifier and remove debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec_tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig

Purpose: defines the Intel WMI platform-driver configuration menu entries used by this directory. It introduces a hidden `INTEL_WMI` boolean selected by concrete WMI drivers, plus tristate options for Slim Bootloader firmware-update signaling and Thunderbolt force-power control.

Important symbols: `INTEL_WMI_SBL_FW_UPDATE` depends on `ACPI_WMI`, selects `INTEL_WMI`, and builds the `intel-wmi-sbl-fw-update` module. `INTEL_WMI_THUNDERBOLT` also depends on `ACPI_WMI`, selects `INTEL_WMI`, and builds `intel-wmi-thunderbolt`.

Control flow/build behavior: this file has no runtime control flow. Kconfig determines whether the corresponding WMI drivers are built in, as modules, or omitted, and ensures the ACPI WMI bus is available before enabling them.

State/persistence: no runtime state. Build selection affects module availability and therefore whether matching WMI GUID devices get sysfs attributes.

Dependencies/integration: integrates with the parent platform/x86 Kconfig tree and the WMI bus. The hidden `INTEL_WMI` symbol can serve as a common grouping symbol for Intel WMI extras.

Risks: both drivers expose platform firmware operations; enabling them makes sysfs controls appear on systems with matching GUIDs. Dependency is intentionally only `ACPI_WMI`, so platform specificity is enforced by WMI GUID matching at runtime.

Test signals: Kconfig resolution should allow `m/y/n` choices for both concrete drivers only when `ACPI_WMI` is available; selected modules should match Makefile targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile

Purpose: maps Intel WMI Kconfig symbols to build targets in this directory.

Important targets: `intel-wmi-sbl-fw-update-y := sbl-fw-update.o` and `obj-$(CONFIG_INTEL_WMI_SBL_FW_UPDATE) += intel-wmi-sbl-fw-update.o`; `intel-wmi-thunderbolt-y := thunderbolt.o` and `obj-$(CONFIG_INTEL_WMI_THUNDERBOLT) += intel-wmi-thunderbolt.o`.

Control flow/build behavior: kernel kbuild composes each module from its single object file when the corresponding config is `m` or links it built-in when `y`.

State/persistence: no runtime state. The target names define module names visible to userspace and modprobe.

Dependencies/integration: must remain in sync with `Kconfig` symbols and source filenames. The selected module names match help text in Kconfig and `wmi_driver.driver.name` values in the C sources.

Risks: typo in target variable naming or config symbol would silently omit a driver or produce unexpected module names. Current file is minimal and direct.

Test signals: `make M=drivers/platform/x86/intel/wmi` with each config enabled should build the expected `.ko` or built-in object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c

Purpose: WMI driver for Intel Slim Bootloader firmware-update signaling. It exposes a `firmware_update_request` sysfs attribute on WMI devices matching GUID `44FADEB1-B204-40F2-8581-394BBDC1B651`, allowing userspace to request an SBL firmware update on next reboot.

Important APIs/functions: `get_fwu_request()` calls `wmidev_query_block()` and decodes a little-endian u32; `set_fwu_request()` calls `wmidev_set_block()` with a little-endian u32. `firmware_update_request_show()` and `_store()` implement the sysfs ABI. The `wmi_driver` uses `dev_groups = firmware_update_groups` and `no_singleton = true`.

Control flow: binding to the WMI GUID logs attachment and automatically creates the sysfs attribute. Reads query WMI block 0 and return the current value. Writes parse an unsigned integer, reject values above 1, and write block 0. Remove only logs detachment.

State/persistence: state lives in firmware/SBL WMI storage, not in the driver. Written value is intended to influence the next reboot firmware update path.

Dependencies/integration: depends on ACPI WMI bus, sysfs device attributes, endian conversion, and SBL firmware implementing the documented GUID/block behavior.

Risks: a write of `1` has firmware-update consequences on reboot; validation restricts values to 0/1 but cannot validate firmware policy. `wmidev_query_block()` allocation is freed with `kfree(result)` after using `buffer.data`.

Test signals: on matching WMI devices, the attribute should read `0` or `1`, reject invalid strings and values >1, and call `wmidev_set_block()` successfully for valid writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c

Purpose: WMI driver exposing a write-only `force_power` sysfs attribute for selected systems with Intel Thunderbolt force-power WMI GUID `86CCFD48-205E-4A77-9C48-2021CBEDE341`. It lets userspace force Thunderbolt controller power for firmware update or maintenance scenarios.

Important APIs/functions: `force_power_store()` parses the first input character with `hex_to_bin()`, accepts only 0 or 1, and calls `wmidev_invoke_procedure()` with method/block identifiers `0, 1`. The `wmi_driver` declares `dev_groups = tbt_groups` and `no_singleton = true`.

Control flow: the WMI core binds matching GUID devices and creates the attribute. Each write constructs a one-byte WMI buffer and invokes the firmware procedure. There is no probe/remove callback because no driver-private state is needed.

State/persistence: requested force-power mode is stored/applied by firmware. The driver maintains no cached state and exposes no readback.

Dependencies/integration: depends on ACPI WMI and sysfs. Consumers are userspace tools that need Thunderbolt power control when no device is attached.

Risks: input parsing only looks at `buf[0]`, so strings beginning with `0` or `1` are accepted regardless of trailing characters. Firmware behavior is platform-specific and may power hardware unexpectedly. No readback means userspace must trust invocation success.

Test signals: matching WMI device should expose `force_power`; writes beginning with `0` or `1` should call the procedure; non-hex or values above 1 should return `-EINVAL`; WMI invocation failures should propagate negative errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/thunderbolt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.c

Purpose: legacy Intel Intelligent Power Sharing driver for Ibex Peak/Westmere-era platforms. It coordinates CPU and integrated GPU turbo behavior within thermal and power budgets by monitoring PCH thermal registers, adjusting CPU turbo power MSRs, and optionally calling exported i915 turbo hooks.

Important APIs/types/functions: `struct ips_driver` stores MMIO mapping, IRQ, monitor/adjust threads, timer, moving averages, limits, turbo flags, i915 function pointers, and original MSR state. `ips_probe()` initializes hardware and threads. `ips_monitor()` samples temperatures/power and updates averages. `ips_adjust()` periodically raises/lowers CPU and GPU clamps. `ips_irq_handler()` handles ME/EC thermal status updates. `ips_get_i915_syms()` dynamically obtains i915 hooks; `ips_link_to_i915_driver()` lets i915 trigger late symbol retry. Debugfs exposes current CPU/MCH temperature, power, and CPU clamp.

Control flow: PCI probe rejects blacklisted systems, detects supported Westmere CPU/SKU, maps the thermal BAR, validates thermal enable/reporting bits, reads BIOS limits, optionally gets i915 hooks, verifies TDP override support, requests INTx IRQ, enables thermal interrupts, saves original turbo limit MSR, disables CPU turbo, creates an adjust thread, then starts the monitor thread. The monitor thread builds an initial 5-second sample window and wakes the adjust thread. The adjust thread every 5 seconds updates BIOS limits if needed, toggles turbo availability, lowers clamps on MCP limit exceedance, otherwise raises or lowers CPU/GPU according to load and budget. Remove stops threads, frees IRQs, releases i915 symbols, and restores turbo MSR state.

State/persistence: live state is MMIO thermal registers, package MSRs, i915 turbo state, moving averages in memory, and debugfs entries. `orig_turbo_limit` is restored on unload. No persistent user configuration exists. Static `late_i915_load` allows late GPU integration after i915 loads.

Dependencies/integration: depends on PCI thermal sensor ID `0x3b32`, x86 MSR access, boot CPU model data, DMI blacklist, kthreads/timers/IRQs, debugfs, and optional exported i915 symbols. The companion header declares the i915 callback entry point.

Risks: the file notes unsupported dual MCP configs and TODO hotplug handling. CPU turbo is forcibly disabled in current logic because power figures are considered wrong. `get_cpu_power()` and `read_mgtv()` currently return 0 despite computing values, reducing effectiveness. MSR writes and thermal clamp changes are high-impact. Thread startup and error unwind must preserve IRQ/MSR cleanup. Dynamic symbol coupling to i915 can disable GPU turbo if any hook is missing.

Test signals: supported Westmere hardware should initialize, create debugfs, start `ips-monitor` and `ips-adjust`, and log ME update stalls if sequence numbers stop. IRQ status writes should acknowledge EC updates and thermal trips. Removing the module should restore `TURBO_POWER_CURRENT_LIMIT`, stop threads, and release all i915 symbols. Unsupported CPU, disabled thermal device, missing TDP override, and DMI-blacklisted systems should fail probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h

Purpose: tiny public companion header for the IPS/i915 integration point.

Important API: declares `void ips_link_to_i915_driver(void);`, exported by `intel_ips.c` and intended for i915 to notify the IPS driver that i915 has loaded and its turbo symbols may now be available.

Control flow: no code. Inclusion lets a GPU driver or related code call the notifier without depending on IPS internals.

State/persistence: no state in the header. The called implementation sets a static `late_i915_load` flag in `intel_ips.c`.

Dependencies/integration: part of the platform/x86 IPS and DRM i915 cooperation path. The symbol is exported GPL-only in the implementation.

Risks: because the API has no instance parameter, the IPS implementation cannot directly address multiple IPS devices and instead uses a global late-load flag.

Test signals: code including this header should compile against the IPS implementation; calling the function should allow `ips_gpu_turbo_enabled()` to retry `symbol_get()` for i915 hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c

Purpose: core driver and exported API for Intel SCU IPC-1 communication. It registers a single SCU IPC device, serializes commands to SCU firmware through MMIO command/status/data registers, and exposes helper calls for PMIC/MSIC register access and generic SCU commands.

Important APIs/types/functions: `struct intel_scu_ipc_dev` wraps a `struct device`, owner module, MMIO base, completion, and platform data. Public get/put APIs manage references and module lifetime. `pwr_reg_rdwr()` implements power-controller read/write/update commands. Exported helpers include `intel_scu_ipc_dev_ioread8()`, `iowrite8()`, `readv()`, `writev()`, `update()`, `simple_command()`, and `command_with_size()`. Registration APIs `__intel_scu_ipc_register()` and `__devm_intel_scu_ipc_register()` create the provider device.

Control flow: subsystem init registers the `intel_scu_ipc` class. A PCI or platform provider calls register with memory and optional IRQ resources. The core reserves and maps MMIO, optionally requests IRQ, registers a device, and stores the singleton `ipcdev`. Command helpers acquire `ipclock`, check for busy status, write input data, issue an IPC command with IOC bit, then wait either for completion interrupt or polling. Results are copied from read buffers and errors are converted to `-EIO`, `-EBUSY`, or `-ETIMEDOUT`.

State/persistence: singleton `ipcdev` and `ipclock` serialize all access. Hardware SCU state persists outside the driver. Device references and module owner pins prevent provider unload while consumers hold the IPC device. Release frees IRQ, unmaps MMIO, releases memory region, and frees the object.

Dependencies/integration: depends on platform data type `intel_scu_ipc_data`, Linux device/class model, completions, MMIO, interrupts, and exported symbols used by other Intel MID/SCU platform drivers. PCI and ACPI platform instantiators feed resources into this core.

Risks: only one IPC instance is supported. Buffer sizes are small hardware-defined windows; command-with-size rejects more than four dwords in or out. `pwr_reg_rdwr()` allows up to five logical register addresses but copies through a fixed 20-byte buffer. Callers may sleep and must not use APIs in atomic context. Interrupt status clearing relies on writing status with `IPC_STATUS_IRQ`.

Test signals: provider registration should create `/sys/class/intel_scu_ipc/intel_scu_ipc`; register access APIs should serialize and return firmware errors; IRQ and polling modes should both complete commands; unregister should set `ipcdev = NULL` and release resources after references drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c

Purpose: legacy character-device utility wrapper around the SCU IPC core. It exposes privileged ioctls for userspace to read, write, and update SCU power-controller registers through `/dev` major registration named `intel_mid_scu`.

Important APIs/types/functions: `struct scu_ipc_data` carries register count, up to five addresses, up to five data bytes, and one mask. `scu_reg_access()` dispatches ioctl commands to SCU IPC core APIs. `scu_ipc_ioctl()` enforces `CAP_SYS_RAWIO` and copies data to/from userspace. Open obtains a singleton SCU IPC device with `intel_scu_ipc_dev_get()`; release puts it.

Control flow: module init allocates a dynamic char major. Open is single-user guarded by `scu_lock` and fails with `-EBUSY` if already open or `-ENODEV` if no core device exists. Ioctl copies the full command structure, validates capability, dispatches, and copies results back. Release clears the global handle.

State/persistence: global `scu` stores the held IPC device while the char device is open; `major` stores the dynamic char major. Register writes affect SCU/PMIC hardware, not driver state.

Dependencies/integration: depends on the SCU IPC core exported APIs, Linux char device registration, user access helpers, and raw IO capability checks.

Risks: powerful raw register access is intentionally privileged. Count validation rejects 0, 3, and >4 despite arrays sized for five, matching legacy ABI expectations but surprising callers. The command constants contain a historical typo prefix `INTE_`.

Test signals: open should fail without an SCU provider and allow only one opener; ioctls should require `CAP_SYS_RAWIO`; read ioctls should update the userspace data array; invalid counts and unknown commands should return `-EINVAL` or `-ENOTTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c

Purpose: built-in PCI instantiator for the Intel SCU IPC core. It binds known Intel SCU PCI device IDs, extracts BAR0 and IRQ resources, and registers the core IPC provider.

Important APIs/functions: `intel_scu_pci_probe()` enables the PCI device with `pcim_enable_device()`, fills `struct intel_scu_ipc_data` from `pdev->resource[0]` and `pdev->irq`, then calls `intel_scu_ipc_register()`. The PCI ID table lists several Intel device IDs including `0x080e`, `0x082a`, `0x08ea`, `0x0a94`, `0x11a0`, `0x1a94`, and `0x5a94`.

Control flow: `builtin_pci_driver()` registers the driver during boot. Probe is minimal and relies on the SCU IPC core for resource reservation, mapping, IRQ request, device registration, and cleanup.

State/persistence: no private state is stored by this wrapper; the core owns the resulting singleton IPC device.

Dependencies/integration: depends on PCI core and `linux/platform_data/x86/intel_scu_ipc.h`. Suppresses bind attributes to avoid manual userspace binding/unbinding for this low-level provider.

Risks: BAR0/IRQ assumptions must match hardware. Since the core supports one IPC instance, multiple matching PCI devices would cause later registration to return `-EBUSY`.

Test signals: matching PCI hardware should register `intel_scu_ipc`; probe should fail cleanly on PCI enable or core registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c

Purpose: ACPI/platform instantiator for the Intel SCU IPC core. It binds ACPI ID `INTC1026`, obtains memory and optional IRQ resources from a platform device, and registers a managed SCU IPC provider.

Important APIs/functions: `intel_scu_platform_probe()` calls `platform_get_irq_optional()`, `platform_get_resource(IORESOURCE_MEM, 0)`, copies the resource into `struct intel_scu_ipc_data`, and calls `devm_intel_scu_ipc_register()`. It stores the returned SCU handle as platform driver data.

Control flow: module platform driver registration handles ACPI matching. Probe fails with `-ENOMEM` when no memory resource is present, propagates managed core registration errors, and otherwise relies on devres for cleanup at device detach.

State/persistence: no custom persistent state beyond platform driver data. The core owns SCU IPC device state and hardware command handling.

Dependencies/integration: integrates ACPI platform discovery, resource APIs, and the SCU IPC core. This is the non-PCI path for platforms that describe SCU through ACPI.

Risks: optional IRQ may be negative, causing the core to use polling mode. Returning `-ENOMEM` for missing memory resource is semantically odd but preserved. The module author string for Mika is missing a closing `>`.

Test signals: ACPI `INTC1026` platform devices with memory resources should create a managed `intel_scu_ipc` core device; detach should unregister automatically via devres.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c

Purpose: platform-device library for Intel Merrifield/Tangier watchdog support. It registers an `intel_mid_wdt` platform device on matching Intel MID CPUs and fills watchdog platform data with an IOAPIC-mapped IRQ.

Important APIs/types/functions: static `wdt_dev` names the platform device. `tangier_probe()` maps GSI `TANGIER_EXT_TIMER0_MSI` to a Linux IRQ using `mp_map_gsi_to_irq()` and stores it in `struct intel_mid_wdt_pdata`. `intel_mid_cpu_ids` matches `INTEL_ATOM_SILVERMONT_MID` and supplies `tangier_pdata`. `register_mid_wdt()` runs at `arch_initcall`.

Control flow: early init matches CPU; if supported, assigns platform data to `wdt_dev` and registers it. The actual watchdog driver later binds `intel_mid_wdt` and calls the pdata probe hook. Exit unregisters the platform device.

State/persistence: static platform device and static platform data live for module/built-in lifetime. The mapped IRQ is stored in pdata after `tangier_probe()`.

Dependencies/integration: depends on x86 CPU matching, IOAPIC/GSI mapping, and `linux/platform_data/x86/intel-mid_wdt.h`. It is a hardware-description bridge, not the watchdog implementation.

Risks: assumes MID IOAPIC identity mapping behavior and GSI 12 for external timer 0. Unsupported CPUs simply return `-ENODEV`. If IOAPIC mapping fails, watchdog probe cannot get an IRQ.

Test signals: on Tangier/Merrifield-class CPU, an `intel_mid_wdt` platform device should appear; calling pdata probe should populate `irq`; unsupported CPUs should not register the device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig

Purpose: defines Lenovo platform/x86 driver configuration options for IdeaPad, ThinkPad, Yoga, and Lenovo WMI extras. It gates each driver on the required kernel subsystems and selects shared support such as sparse keymaps, LEDs, platform profile, hwmon, firmware attributes, and WMI helper modules.

Important symbols: `IDEAPAD_LAPTOP` depends on ACPI, ACPI battery, rfkill/input, i8042, backlight, and optional ACPI video/WMI compatibility. ThinkPad options include `THINKPAD_ACPI` plus debug, ALSA, unsafe LED, video, and hotkey polling suboptions. Lenovo WMI options include hotkey utilities, camera, YMC tablet mode, GameZone, tuning, capdata/events/helpers, YogaBook, and Yoga Tablet fast charge.

Control flow/build behavior: no runtime logic. Kconfig resolution controls which modules are visible and guarantees required frameworks are present before drivers compile.

State/persistence: no runtime state. Choices affect module availability and which sysfs/input/platform-profile features can be present on Lenovo hardware.

Dependencies/integration: integrates with ACPI, ACPI_WMI, DMI, input, rfkill, backlight, LEDs, DRM, hwmon, firmware-attributes, extcon, serial device bus, and platform-profile frameworks.

Risks: dependency expressions like `ACPI_WMI || ACPI_WMI = n` permit building without WMI but avoid impossible combinations. User-visible help text for ThinkPad video includes old cautionary language but documents real interaction risks.

Test signals: configuration should expose only valid combinations; enabling each symbol should produce the Makefile module names and satisfy selected helper dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile

Purpose: kbuild mapping for Lenovo platform/x86 drivers, including direct object targets and a macro that prefixes several WMI/Yoga modules with `lenovo-`.

Important targets: direct targets include `ideapad-laptop.o`, `think-lmi.o`, and `thinkpad_acpi.o`. `lenovo-target-*` collects modules such as `wmi-hotkey-utilities`, `ymc`, `yogabook`, `yoga-tab2-pro-1380-fastcharger`, `wmi-camera`, `wmi-capdata`, `wmi-events`, `wmi-helpers`, `wmi-gamezone`, and `wmi-other`. `LENOVO_OBJ_TARGET` rewrites each into `lenovo-<target>.o` with a single contained object.

Control flow/build behavior: kbuild expands the macro separately for built-in and module targets using `foreach` over the basename of selected target lists.

State/persistence: no runtime state. It defines user-visible module filenames for Lenovo WMI/Yoga helper drivers.

Dependencies/integration: must stay aligned with Kconfig symbol names and source filenames in the directory.

Risks: macro indirection improves naming consistency but can obscure missing source/object mismatches. Direct targets and prefixed targets use different naming conventions intentionally.

Test signals: building selected configs should produce `ideapad-laptop` directly and `lenovo-wmi-*`/`lenovo-ymc` style prefixed modules for macro-managed targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.c

Purpose: Lenovo IdeaPad ACPI extras driver. It exposes firmware-backed controls for rfkill, camera, touchpad, fan, battery charge modes, USB charging, keyboard backlight, FnLock LED, vendor backlight, hotkeys, platform profile/DYTC performance modes, and WMI key events.

Important APIs/types/functions: `struct ideapad_private` is the central per-device state, including ACPI handle, VPC/GBMD mutexes, rfkill devices, input device, backlight, DYTC state, debugfs, battery hook/extension, `_CFG`, feature flags, and LED state. ACPI helpers wrap `_CFG`, `VPCR/VPCW`, `GBMD/SBMC`, `HALS/SALS`, `KBLC`, and `DYTC`. Sysfs attributes cover `camera_power`, deprecated `conservation_mode`, `fan_mode`, `fn_lock`, `touchpad`, and `usb_charging`. Power-supply extensions expose `POWER_SUPPLY_PROP_CHARGE_TYPES`. Exported notifier APIs in namespace `IDEAPAD_LAPTOP` support YMC interaction.

Control flow: module init registers optional WMI driver first, then the ACPI platform driver for `VPC2004`. Probe reads `_CFG`, initializes mutexes, detects feature support by ACPI methods, HALS/GBMD bits, DMI quirks, and module parameters, creates debugfs/input/LEDs/rfkill, syncs rfkill and touchpad state, initializes DYTC platform-profile support when usable, optionally registers vendor backlight, installs ACPI notify handler, initializes global shared state, and registers an internal notifier. ACPI notify reads VPC event bitmaps and dispatches hotkeys, rfkill sync, touchpad sync, backlight updates, Novo key, keyboard backlight update, and special buttons. WMI notify reports Esc/Fn-key events and cycles platform profile for performance key events.

State/persistence: state is mostly firmware-backed through EC/ACPI methods. Driver caches feature flags, last touchpad value, last LED brightness, current platform profile, and global `ideapad_shared` for WMI/notifier bridging. Module parameters enable risky model-specific paths (`allow_v4_dytc`, hardware rfkill switch, FnLock LED setting, PS/2 aux control, touchpad EC sysfs, YMC EC trigger). Remove unregisters all interfaces and clears shared state.

Dependencies/integration: depends on ACPI, ACPI battery hooks, ACPI video backlight policy, optional ACPI WMI, input sparse keymap, rfkill, LED class, backlight class, platform-profile, power-supply extensions, i8042, DMI quirks, and debugfs. It coordinates with `lenovo-ymc` via exported notifier calls.

Risks: EC polling is rate-limited because frequent polling can hard-shutdown some newer ThinkBooks. Many capabilities are firmware/model-specific and guarded by DMI/module params. `ideapad_shared` supports only one platform device, so multiple VPC devices are rejected. Backlight/rfkill/touchpad paths can make hardware unusable if incorrectly enabled, which is why hardware rfkill and PS/2 aux control default off. Charge modes are made mutually exclusive, but firmware can still report both as enabled and then driver returns `-EINVAL`.

Test signals: supported systems should expose only feature-visible sysfs attributes; rfkill devices should reflect `_CFG` capabilities and hardware switch state; battery `charge_types` should switch Standard/Fast/Long Life through SBMC; DYTC platform profile should get/set low-power/balanced/performance and notify on refresh; ACPI/WMI hotkeys should report expected input scancodes; suspend/resume should resync rfkill, touchpad, and DYTC state; remove should unregister LEDs, input, rfkill, backlight, debugfs, and notifiers without stale shared pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h

Purpose: public internal header for the Lenovo IdeaPad notifier interface used by companion Lenovo platform drivers, especially Yoga Mode Control integration.

Important APIs/types: `enum ideapad_laptop_notifier_actions` currently defines `IDEAPAD_LAPTOP_YMC_EVENT`. The header declares `ideapad_laptop_register_notifier()`, `ideapad_laptop_unregister_notifier()`, and `ideapad_laptop_call_notifier()`.

Control flow: no implementation here. `ideapad-laptop.c` backs the declarations with a blocking notifier chain and exports the functions in namespace `IDEAPAD_LAPTOP`.

State/persistence: no header state. Consumers register notifier blocks; the implementation stores them in the blocking notifier chain.

Dependencies/integration: depends only on `linux/notifier.h`. It decouples companion modules from the full IdeaPad private structure while allowing YMC events to trigger IdeaPad EC workarounds.

Risks: the action enum is currently narrow; expanding it requires coordinated implementation handling. Consumers must obey notifier-block lifetime rules and unregister before unload.

Test signals: companion modules should compile by including this header and importing namespace `IDEAPAD_LAPTOP`; notifier registration should receive `IDEAPAD_LAPTOP_YMC_EVENT` when `ideapad_laptop_call_notifier()` is invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h -->
