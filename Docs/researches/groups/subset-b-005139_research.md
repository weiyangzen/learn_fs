# Research: subset-b-005139 Intel platform x86 PMT, Speed Select, telemetry, TPMI, and uncore files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery.c

## Purpose

This file implements the Intel Platform Monitoring Technology feature-discovery auxiliary driver. It consumes `intel_vsec.discovery` resources, decodes PMT feature discovery tables, creates one sysfs kobject per supported feature under the PMT class device, and exports discovered feature metadata so PMT telemetry entries can be tagged with feature flags.

## Important APIs, Types, And Functions

Core internal types are `struct feature_discovery_table`, `struct feature_header`, `struct feature_table`, `struct feature`, and `struct pmt_features_priv`. `pmt_feature_get_disc_table()` maps each discovery resource, rejects duplicate IDs, skips reserved/zero-size/too-new/invalid features, and records the ID in `priv->mask`. `pmt_feature_get_feature_table()` maps the actual feature table for `ACCESS_LOCAL`, validates table size against the resource, copies attributes and GUIDs, and fills `feature->table`. `pmt_features_discovery()` chooses the sysfs attribute layout from `feature_layout[]`, initializes the feature kobject, emits the add uevent, and links it into the global list. `intel_pmt_get_features()` is the exported PMT namespace function used by telemetry entries to match entry GUIDs against discovered feature GUID lists.

## Control Flow

The auxiliary driver binds to `intel_vsec.discovery`. Probe creates a PMT class child named `features-<parent>`, iterates all VSEC resources, decodes each discovery table, skips benign unsupported entries, initializes kobjects for valid entries, and increments `priv->count` only after full setup. Sysfs reads dispatch through layout-specific kobject types: RMID features expose caps, `num_rmids`, watcher period, command sizes, and GUIDs; watcher and command layouts expose only applicable command/watcher fields; caps-only layouts expose caps and GUIDs. Removal walks fully initialized entries, removes list membership and sysfs groups, drops kobject refs, and unregisters the child device.

## State And Persistence

Runtime state is the `pmt_features_priv` allocation, per-feature kobjects, devm-allocated GUID arrays, and global `pmt_feature_list` protected by `feature_list_lock`. The driver stores no persistent on-disk state. Hardware table contents are read-only MMIO snapshots; discovered feature associations last only until the auxiliary device is removed.

## Dependencies And Integration Points

The file depends on the auxiliary bus, Intel VSEC resource enumeration, PMT class support from `class.h`, PMT feature definitions from `linux/intel_pmt_features.h`, sysfs/kobject APIs, and exported PMT namespace consumers. It imports `INTEL_PMT` and exports `intel_pmt_get_features()` in that namespace.

## Risks

The table decoder currently supports only `ACCESS_LOCAL`; future BAR-based feature tables would fail probe. `pmt_feature_get_disc_table()` indexes `pmt_feature_names[disc_tbl->id]` for duplicate reporting before validating the ID, so malformed duplicate IDs outside the enum would be sensitive to discovery table integrity. The empty kobject release is acceptable because feature memory is devm-owned, but lifetime expectations must remain aligned with device removal. Feature GUID matching is parent-device scoped, so incorrect parent pointers would under- or over-tag telemetry entries.

## Test Signals

Good signals are successful probe on `intel_vsec.discovery`, sysfs feature directories named from `pmt_feature_names[]`, correct per-layout attributes, duplicate-feature rejection, reserved/zero-size skip behavior, `intel_pmt_get_features()` adding flags and RMID counts to PMT telemetry entries, and clean kobject/sysfs teardown on module unload or device unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/features.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/features.c

## Purpose

This file is the static PMT discovery metadata catalog. It maps `enum pmt_feature_id` values to sysfs-visible feature names, declares each feature's attribute layout, and defines capability-bit name tables used by `discovery.c` when rendering the `caps` sysfs file.

## Important APIs, Types, And Functions

The exported arrays are `pmt_feature_names[]`, `feature_layout[]`, and the feature-specific `struct pmt_cap` arrays such as `pmt_cap_common`, `pmt_cap_pcpt`, `pmt_cap_pcet`, `pmt_cap_crashlog`, `pmt_cap_tpmi`, `pmt_cap_tracing`, and `pmt_cap_rmid_energy`. Each exported `pmt_caps_*[]` pointer array combines common capability names with feature-specific capability names and terminates with `NULL`.

## Control Flow

There is no runtime control flow beyond static data access. Discovery sysfs code selects the appropriate `pmt_caps_*[]` array based on feature ID and walks nested capability arrays until a zero-name terminator, printing whether each mask bit is present in the hardware-reported capability word.

## State And Persistence

All state is static process memory and effectively immutable after module load. There is no hardware access and no persistence.

## Dependencies And Integration Points

The file depends on `linux/intel_pmt_features.h` for feature IDs, layout enums, and capability masks. `pmt_feature_names` is exported in `INTEL_PMT_DISCOVERY`; the capability arrays are included by PMT discovery code through the public feature header.

## Risks

The arrays rely on enum-index alignment. Adding a new `enum pmt_feature_id` without updating names, layouts, and capability tables will produce missing sysfs naming or incorrect attribute selection. Capability names are user-visible ABI-ish debug information, so spelling or mask mistakes mislead tools.

## Test Signals

Build coverage catches missing enum or mask definitions. Runtime signals include `caps` output containing common and feature-specific names, valid sysfs directory names for all discovered IDs, and no out-of-bounds access when discovery exposes every supported PMT feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.c

## Purpose

This file implements the Intel PMT telemetry auxiliary driver. It creates PMT telemetry endpoints from Intel VSEC telemetry resources, exposes endpoint handles through an xarray, provides exported endpoint registration/read APIs for in-kernel clients, and provides a feature-query API returning telemetry regions grouped by PMT feature ID.

## Important APIs, Types, And Functions

Important types include `struct pmt_telem_priv`, `struct telem_endpoint`, `struct intel_pmt_entry`, and `struct pmt_feature_group`. The PMT namespace callbacks are `pmt_telem_header_decode()` and `pmt_telem_add_endpoint()`. Public APIs are `pmt_telem_get_next_endpoint()`, `pmt_telem_register_endpoint()`, `pmt_telem_unregister_endpoint()`, `pmt_telem_get_endpoint_info()`, `pmt_telem_find_and_register_endpoint()`, `pmt_telem_read()`, `pmt_telem_read32()`, `intel_pmt_get_regions_by_feature()`, and `intel_pmt_put_feature_group()`.

## Control Flow

Probe binds to `intel_vsec.telemetry`, allocates storage for all possible resources, and calls `intel_pmt_dev_create()` under `ep_lock` for each resource. The PMT class helper decodes discovery headers, maps telemetry MMIO, and stores entries in `telem_array`. After a successful entry is created, `intel_pmt_get_features()` annotates it using the discovery driver's feature list. Clients enumerate endpoint IDs with `pmt_telem_get_next_endpoint()`, get a kref with `pmt_telem_register_endpoint()`, read qwords or dwords by sample ID, and release with `pmt_telem_unregister_endpoint()`. Removal marks endpoints absent through `intel_pmt_dev_destroy()` and drops endpoint krefs.

## State And Persistence

`telem_array` is the global endpoint index protected by `ep_lock`. Each endpoint has a kref, `present` flag, MMIO base, header, device pointer, and optional VSEC read callback. Feature-region queries allocate a kref-counted `pmt_feature_group` snapshot. State is volatile and tied to auxiliary device lifetime; no persistent state is stored.

## Dependencies And Integration Points

The file integrates with Intel VSEC, PMT class helper code, PMT discovery, xarray, kref, auxiliary bus, and the `INTEL_PMT_TELEMETRY` exported namespace. `pmt_copy_region()` uses `intel_vsec_get_mapping()` and PCI parent platform data to build OOB telemetry region descriptors.

## Risks

Endpoint reads rely on callers honoring alignment and count semantics. `pmt_telem_read()` checks `present` before and after MMIO access, returning `-EPIPE` if removal raced with the read, but copied data must then be considered invalid. The xarray stores `intel_pmt_entry` pointers while endpoint krefs manage only `entry->ep`, so class helper teardown must remove xarray entries before freeing entry storage. Early-client overlap detection skips fixed telemetry blocks for some hardware, so device-specific GUID/type handling is sensitive.

## Test Signals

Useful tests include endpoint enumeration, endpoint info retrieval, qword and dword bounds checks, removal races returning `-ENODEV` or `-EPIPE`, feature-group queries for valid and invalid IDs, successful import/export namespace linkage, and telemetry reads through both direct MMIO and any VSEC callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.h

## Purpose

This header defines the public in-kernel PMT telemetry endpoint interface used by clients that need to enumerate, register, inspect, and read PMT telemetry endpoints.

## Important APIs, Types, And Functions

It defines telemetry type constants `PMT_TELEM_TELEMETRY` and `PMT_TELEM_CRASHLOG`, `struct telem_header`, and `struct telem_endpoint_info`. It declares `pmt_telem_get_next_endpoint()`, `pmt_telem_register_endpoint()`, `pmt_telem_unregister_endpoint()`, `pmt_telem_get_endpoint_info()`, `pmt_telem_find_and_register_endpoint()`, `pmt_telem_read()`, and `pmt_telem_read32()`.

## Control Flow

The intended flow is: iterate endpoint IDs, fetch endpoint info if needed, register an endpoint to increment its kref, perform aligned sample reads by sample ID, and unregister when done. `pmt_telem_find_and_register_endpoint()` combines lookup by device, GUID, and instance position.

## State And Persistence

The header owns no state. It documents that endpoint pointers carry a kref in the implementation and that `-ENODEV` from reads indicates a removed endpoint requiring unregister.

## Dependencies And Integration Points

The declarations are implemented by `pmt/telemetry.c` and used by PMT telemetry consumers. The API exposes only opaque `struct telem_endpoint *` plus endpoint metadata.

## Risks

The comments say `pmt_telem_read32()` reads qwords even though it operates on dwords; this documentation mismatch can confuse callers. The API relies on callers to allocate sufficiently large buffers and request in-bounds aligned sample ranges.

## Test Signals

Compile tests for telemetry consumers, endpoint enumeration tests, and read-path tests for invalid IDs, removed endpoints, and out-of-range offsets validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/punit_ipc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/punit_ipc.c

## Purpose

This file implements the Intel P-Unit IPC mailbox driver used by other platform drivers to issue BIOS, ISP, and GT driver power-management commands through ACPI-provided MMIO resources.

## Important APIs, Types, And Functions

The central state type is `IPC_DEV`, stored globally as `punit_ipcdev`. `intel_punit_ipc_command()` is the exported API. It serializes commands with `ipcdev->lock`, writes optional input data, formats command parameters into the interface register, waits for completion by IRQ or polling, decodes firmware error status, and reads optional output data. `intel_punit_get_bars()` maps required BIOS IPC data/interface resources and optional ISP/GT resources. `intel_punit_ioc()` completes IRQ-driven commands.

## Control Flow

`fs_initcall()` registers the ACPI platform driver early for `INT34D4`. Probe allocates global state, optionally requests an IRQ, maps MMIO bars, initializes the mutex/completion, and leaves the exported API available. Callers encode command type in the command word; the driver selects the mailbox type, handles two-word data for GT/ISP commands, starts the transaction, and blocks until the run bit clears or interrupt completion fires.

## State And Persistence

Runtime state is a singleton device pointer, per-mailbox MMIO base array, one mutex, one completion, and optional IRQ. There is no remove callback and no persistent storage. Hardware mailbox state is transient; command side effects belong to firmware/platform power state.

## Dependencies And Integration Points

The driver depends on ACPI platform enumeration, platform MMIO resources, Linux completion/IRQ APIs, and `asm/intel_punit_ipc.h` for IPC command types and error codes. Legacy telemetry platform code uses this exported command function for PSS telemetry setup and trace controls.

## Risks

There is no explicit NULL check in `intel_punit_ipc_command()` for `punit_ipcdev`, so consumers must load/probe after this early driver. Optional GT/ISP resources may remain NULL; callers issuing those command types on hardware without optional mappings could fault. Polling mode busy-waits up to one second. The singleton design does not support multiple devices.

## Test Signals

Tests should cover ACPI probe, required resource mapping failures, optional resource absence, IRQ and polling completion, timeout behavior, firmware error-code reporting, exported-symbol consumers, and telemetry commands that read/write PSS telemetry registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/punit_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/rst.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/rst.c

## Purpose

This driver exposes Intel Rapid Start Technology ACPI controls through two sysfs attributes on the matched ACPI companion device.

## Important APIs, Types, And Functions

`irst_show_wakeup_events()` and `irst_store_wakeup_events()` wrap ACPI methods `GFFS` and `SFFS`. `irst_show_wakeup_time()` and `irst_store_wakeup_time()` wrap `GFTV` and `SFTV`. Probe creates `wakeup_time` and `wakeup_events` device attributes, and remove deletes them.

## Control Flow

The platform driver matches ACPI ID `INT3392`. Probe creates `wakeup_time` first, then `wakeup_events`; failure to create the second rolls back the first. User reads evaluate ACPI integer methods; user writes parse an unsigned long and execute the matching ACPI simple method.

## State And Persistence

The driver stores no private state. Values persist only through firmware/ACPI state managed by platform firmware.

## Dependencies And Integration Points

It depends on ACPI companion devices, platform driver binding, and sysfs device attributes. The interface is firmware-defined through four ACPI methods.

## Risks

The attributes are mode `0600`, limiting access to privileged users, but values are passed directly to firmware after numeric parsing. ACPI method absence or firmware failure is collapsed to `-EINVAL`, which can obscure diagnostics. The code uses `sprintf()` rather than `sysfs_emit()`, matching older style but less preferred.

## Test Signals

Probe on `INT3392`, existence of both sysfs files, successful reads/writes against known firmware, rollback on attribute creation failure, and clean remove are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/rst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/sdsi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/sdsi.c

## Purpose

This file implements the Intel On Demand / Software Defined Silicon auxiliary driver. It maps SDSi mailbox/register regions discovered by Intel VSEC, exposes provisioning and certificate/register binary sysfs files, and performs in-band mailbox transactions using required 64-bit MMIO accesses.

## Important APIs, Types, And Functions

Key types are `struct sdsi_priv`, `struct sdsi_mbox_info`, and `struct disc_table`. Mailbox helpers include `sdsi_mbox_acquire()`, `sdsi_mbox_cmd_write()`, `sdsi_mbox_cmd_read()`, `sdsi_mbox_poll()`, and `sdsi_complete_transaction()`. User-facing sysfs handlers are `provision_akc_write()`, `provision_cap_write()`, `state_certificate_read()`, `meter_certificate_read()`, `meter_current_read()`, `registers_read()`, and `guid_show()`. Probe uses `sdsi_get_layout()` and `sdsi_map_mbox_registers()`.

## Control Flow

Probe binds to `intel_vsec.sdsi`, reads the discovery table, selects layout based on SDSi GUID v1 or v2, maps the SDSi region from either local discovery-relative addressing or PCI BAR addressing, and reads feature bits. Sysfs visibility always exposes `registers`; provisioning and certificate files require the SDSi feature bit, and metering files additionally require the metering bit. Provision writes reject nonzero offsets, check in-band lock, build a qword-aligned payload with the command in the final qword, acquire the mailbox, write the payload, and poll completion. Certificate reads acquire the mailbox, issue a read command, collect up to four 1 KiB packets, and copy the result to sysfs.

## State And Persistence

`sdsi_priv` holds the mailbox mutex, mapped control/mailbox/register pointers, selected layout sizes, GUID, and feature bits. There is no persistent software storage. Provisioning commands can have persistent platform/license effects in hardware or firmware; the driver only transports the payload.

## Dependencies And Integration Points

The driver integrates with Intel VSEC auxiliary devices, PCI resources, sysfs binary attributes, admin-only bin attributes, `readq_poll_timeout()`, and strict 64-bit MMIO copy helpers. It relies on firmware mailbox ownership and status protocol.

## Risks

Provisioning is security-sensitive and irreversible on some platforms, so visibility gating and `BIN_ATTR_ADMIN_RO`/write-only permissions are important. `sdsi_mbox_acquire()` can take several retries after recent transactions. Packet-size, EOM, and total-message validation protect against firmware protocol errors, but malformed firmware responses still result in partial warnings or `-EPROTO`. A typo in `maibox_size` is harmless because the field is unused. Layout and access-type decoding must match VSEC discovery exactly.

## Test Signals

Signals include correct sysfs file visibility from feature bits, GUID v1/v2 layout mapping, register reads clipped to actual size, provisioning rejects nonzero offsets and locked mailboxes, mailbox timeout/ownership/status paths, multi-packet certificate reads, and admin permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/sdsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/smartconnect.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/smartconnect.c

## Purpose

This small ACPI platform driver disables Intel Smart Connect when firmware reports that the operating system has support responsibility.

## Important APIs, Types, And Functions

`smartconnect_acpi_probe()` evaluates ACPI method `GAOS`; if bit 0 is set, it logs a message and executes `SAOS` with value 0. The ACPI match table contains `INT33A0`.

## Control Flow

On platform probe, the driver gets the ACPI handle, reads `GAOS`, returns `-EINVAL` if evaluation fails, and otherwise attempts the disabling write only when the OS-available bit is set. It does not implement remove because it does not maintain state.

## State And Persistence

The driver stores no state. The only persistent behavior is firmware/platform Smart Connect state modified by `SAOS`.

## Dependencies And Integration Points

It depends on ACPI method semantics and Linux platform-driver ACPI matching.

## Risks

If `SAOS` fails, the current code ignores the failure and returns success. There is no rollback or later verification. The driver assumes `GAOS` bit 0 is the only needed policy signal.

## Test Signals

Probe on `INT33A0`, `GAOS` failure handling, log emission when disabling, and firmware-visible `SAOS(0)` execution are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/smartconnect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Kconfig

## Purpose

This Kconfig fragment defines build options for Intel Speed Select Technology interface drivers.

## Important APIs, Types, And Functions

`INTEL_SPEED_SELECT_INTERFACE` is the user-visible tristate. `INTEL_SPEED_SELECT_TPMI` is an internal tristate selected when `INTEL_TPMI` is enabled. The menu depends on `PCI` and `X86_64 || COMPILE_TEST`.

## Control Flow

Selecting the interface builds the common char-device layer plus MMIO, PCI mailbox, MSR mailbox, and, when TPMI is configured, TPMI Speed Select modules.

## State And Persistence

Kconfig has no runtime state; it controls build inclusion.

## Dependencies And Integration Points

The option integrates with the platform/x86 Intel build, PCI, TPMI, and userspace tooling that expects `/dev/isst_interface`.

## Risks

The TPMI suboption is hidden and selected only through `INTEL_TPMI`; disabling TPMI removes the newer backend even when the main interface is enabled. The help text describes non-architectural Xeon server features, so enabling on unsupported hardware should rely on runtime CPU/device checks.

## Test Signals

Configuration tests should verify module objects built for `m`, built-in behavior for `y`, and TPMI object inclusion only when `INTEL_TPMI` is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Makefile

## Purpose

This Makefile maps Speed Select Kconfig symbols to module objects.

## Important APIs, Types, And Functions

`CONFIG_INTEL_SPEED_SELECT_INTERFACE` builds `isst_if_common.o`, `isst_if_mmio.o`, `isst_if_mbox_pci.o`, and `isst_if_mbox_msr.o`. `CONFIG_INTEL_SPEED_SELECT_TPMI` builds `isst_tpmi_core.o` and `isst_tpmi.o`.

## Control Flow

There is no runtime control flow; Kbuild uses these object lists to compile and link the selected modules.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The object ordering separates common char-device code, legacy backends, and TPMI backend glue/core.

## Risks

Because common and backend objects are independent modules, namespace exports and module load ordering matter. Missing common module prevents backend registration with `/dev/isst_interface`.

## Test Signals

Build with interface only and interface plus TPMI, inspect produced modules, and run modprobe dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.c

## Purpose

This file implements the common Intel Speed Select userspace interface. It creates `/dev/isst_interface`, tracks registered backend callbacks, validates and dispatches ioctls, maps logical CPUs to P-unit/PCI topology, and stores selected write commands for replay after resume.

## Important APIs, Types, And Functions

Exports include `isst_if_cdev_register()`, `isst_if_cdev_unregister()`, `isst_if_get_pci_dev()`, `isst_if_mbox_cmd_invalid()`, `isst_if_mbox_cmd_set_req()`, `isst_store_cmd()`, and `isst_resume_common()`. Internal state includes `punit_callbacks[]`, `isst_cpu_info`, `isst_pkg_info`, and the `isst_hash` command replay table. `isst_if_def_ioctl()` handles platform info, CPU map, MMIO, mailbox, MSR, and backend default ioctls. `isst_if_exec_multi_cmd()` handles batched user commands with a maximum of 64.

## Control Flow

Module init checks CPU model support. For legacy mailbox-only Skylake-X it verifies OS mailbox MSRs; for HPM platforms it blocks legacy non-TPMI backends. It initializes CPU topology via a dynamic CPU hotplug state and registers the misc device. Backends register callbacks for MBOX, MMIO, or TPMI. On open, module refs are taken for registered backends; ioctl dispatch copies each command from userspace, invokes the registered callback, and copies results back unless the callback marks it write-only. Resume replay iterates stored writes and reissues mailbox or MSR writes.

## State And Persistence

State is in global callback slots, CPU/package topology caches, misc-device open count, API version, and replay hash. Replay state persists only in memory across suspend/resume, not reboot. The open lock prevents backend registration changes while userspace has the device open.

## Dependencies And Integration Points

The file integrates with `uapi/linux/isst_if.h`, x86 CPU matching, cpuhotplug, PCI enumeration, MSR access, miscdevice, module references, and backend modules. It uses MSR `0x128`, `MSR_THREAD_ID_INFO`, and `MSR_PM_LOGICAL_ID` for topology.

## Risks

The shared global callback slots mean multiple devices of the same backend type can conflict; registration fails if the device is open but replacement behavior otherwise is coarse. Topology mapping depends on NUMA and PCI bus numbering heuristics. Only whitelisted mailbox and MSR commands are allowed; stale whitelists can block new features or allow unsafe ones. `isst_if_relase` is misspelled but wired correctly as `.release`.

## Test Signals

Test `/dev/isst_interface` creation, `ISST_IF_GET_PLATFORM_INFO`, batched command limits, logical-to-P-unit CPU mapping, invalid command rejection, CAP_SYS_ADMIN enforcement for writes, backend registration/unregistration while open, suspend/resume replay, and unsupported CPU model `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.h

## Purpose

This internal header shares Speed Select device IDs, MSR addresses, device-type constants, callback structure, and helper prototypes between the common interface and backend drivers.

## Important APIs, Types, And Functions

`struct isst_if_cmd_cb` describes backend ioctl handlers, command sizes, user buffer offsets, API version, owner module, per-command callback, and optional default ioctl callback. Constants include `ISST_IF_CMD_LIMIT`, API/driver versions, backend IDs, PCI device IDs, and OS mailbox MSRs.

## Control Flow

Backends fill `struct isst_if_cmd_cb` and call `isst_if_cdev_register()`. The common ioctl path uses `cmd_size`, `offset`, and callback pointers to dispatch user requests.

## State And Persistence

The header itself has no state; it defines contracts for shared global state in `isst_if_common.c`.

## Dependencies And Integration Points

It depends on UAPI command structures and is included by MMIO, PCI mailbox, MSR mailbox, and TPMI core code.

## Risks

The callback contract requires correct `offset` and `cmd_size`; mistakes would copy the wrong bytes from userspace. `ISST_IF_CMD_LIMIT` bounds latency and memory use, so UAPI changes must respect it.

## Test Signals

Compile all backends, check API version reported through platform info, and exercise each backend's registered callback through the common ioctl path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_msr.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_msr.c

## Purpose

This backend implements Intel Speed Select mailbox commands through OS mailbox MSRs on Skylake-X style platforms.

## Important APIs, Types, And Functions

`isst_if_send_mbox_cmd()` performs the two-MSR mailbox transaction using `MSR_OS_MAILBOX_INTERFACE` and `MSR_OS_MAILBOX_DATA`. `msrl_update_func()` runs the transaction on the target CPU. `isst_if_mbox_proc_cmd()` validates commands, enforces CAP_SYS_ADMIN for set requests, dispatches with `smp_call_function_single()`, stores set commands for resume, and returns response data. A PM notifier calls `isst_resume_common()` after suspend/hibernate/restore.

## Control Flow

Module init matches `INTEL_SKYLAKE_X`, verifies mailbox MSRs, registers a MBOX callback with the common interface, and installs a PM notifier. User mailbox ioctls enter common code, then this backend executes on the requested logical CPU to avoid cross-CPU MSR races.

## State And Persistence

The backend stores no per-device state. Resume persistence is delegated to the common replay hash. Firmware mailbox state is transient.

## Dependencies And Integration Points

It depends on x86 MSR access, CPU model matching, suspend notifiers, common ISST validation/storage helpers, and the `/dev/isst_interface` callback path.

## Risks

The retry count is intentionally small because MSR overhead is expected to cover firmware latency; slow firmware can return `-EBUSY`. Commands are executed on user-selected CPUs, so CPU hotplug and invalid logical IDs must be validated by common helper logic. All mailbox failures with low response byte set are collapsed to `-ENXIO`.

## Test Signals

MSR presence checks, invalid command rejection, set-request privilege checks, response-data reads, resume replay, CPU offline/online behavior, and busy-bit timeout handling are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_pci.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_pci.c

## Purpose

This backend implements Speed Select P-unit mailbox commands through PCI config-space registers on CFG mailbox devices.

## Important APIs, Types, And Functions

`struct isst_if_device` holds a per-PCI-device mutex. `isst_if_mbox_cmd()` polls the mailbox busy bit, writes request data and command fields to PCI config offsets `0xA0` and `0xA4`, then polls completion and reads response data. `isst_if_mbox_proc_cmd()` validates the user command, locates the PCI device for the target CPU via `isst_if_get_pci_dev(cpu, 1, 30, 1)`, serializes with the device mutex, and stores set commands for resume.

## Control Flow

The PCI driver matches Intel CFG mailbox device IDs. Probe enables the device, allocates state, registers the MBOX callback, and remove unregisters it. Runtime ioctls flow through common code into `isst_if_mbox_proc_cmd()`. Device PM resume calls `isst_resume_common()`.

## State And Persistence

Per-device state is just a mutex in PCI drvdata. Common replay state persists writes across suspend. Hardware config-space mailbox state is transient.

## Dependencies And Integration Points

It integrates with PCI probe/remove/PM, common ISST topology mapping, common ioctl dispatch, command validation, and CAP_SYS_ADMIN policy.

## Risks

Only one global MBOX callback slot exists, so multi-device registration is coarse even though each PCI device has its own mutex. Mailbox polling uses a one-millisecond max timeout with rescheduling after typical latency; long firmware stalls can produce `-EBUSY`. Correct CPU-to-PCI mapping is critical.

## Test Signals

PCI ID probe, `/dev/isst_interface` MBOX support, valid command response, invalid command rejection, set-command privilege and replay, suspend/resume replay, and timeout paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mmio.c

## Purpose

This backend exposes selected Speed Select P-unit MMIO registers through the common ioctl interface for RAPL priority devices.

## Important APIs, Types, And Functions

`struct isst_if_device` stores the mapped P-unit MMIO base, valid register ranges, suspend snapshots, and a mutex. `isst_if_mmio_rd_wr()` validates register alignment and range, enforces CAP_SYS_ADMIN for writes, finds the PCI device for the target CPU, and performs serialized `readl()` or `writel()`. Probe computes the base address from PCI config registers `0xD0` and `0xFC`, maps the selected range, and registers the MMIO callback. PM ops save and restore configured ranges.

## Control Flow

The PCI driver matches RAPL priority device IDs with different range tables. Runtime ioctls dispatch through the common `ISST_IF_IO_CMD` path. Suspend snapshots both allowed ranges; resume writes them back.

## State And Persistence

State is per PCI device and includes cached register snapshots used for suspend/resume restoration. User writes are hardware state and may be restored after system sleep.

## Dependencies And Integration Points

The file depends on PCI config access, ioremap resource handling, common ISST CPU-to-PCI mapping, and common char-device callbacks.

## Risks

Range validation checks only the overall first-begin to second-end interval, not holes between ranges, so an address in the gap could pass if hardware exposes one. Base address calculation is device-specific and sensitive to config format. Multiple devices share one common MMIO callback slot.

## Test Signals

Probe on both device IDs, mapping address correctness, aligned read/write ioctls, rejection of unaligned/out-of-range writes, privilege enforcement, and suspend/resume state restoration are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi.c

## Purpose

This is the auxiliary-bus glue driver for Intel Speed Select over TPMI. It binds VSEC-created `intel_vsec.tpmi-sst` devices to the shared TPMI SST core.

## Important APIs, Types, And Functions

`intel_sst_probe()` calls `tpmi_sst_init()` then `tpmi_sst_dev_add()`. `intel_sst_remove()` removes the device and decrements core usage. PM callbacks delegate to `tpmi_sst_dev_suspend()` and `tpmi_sst_dev_resume()`.

## Control Flow

The auxiliary driver registers through `module_auxiliary_driver()`. Probe initializes common TPMI char-device support once and adds the package/partition device. Remove reverses the device and core registration. Sleep PM saves/restores SST controls through the core.

## State And Persistence

This file stores no state itself. State lives in `isst_tpmi_core.c`.

## Dependencies And Integration Points

It imports `INTEL_TPMI_SST`, depends on Intel TPMI auxiliary enumeration, and connects device PM to the core.

## Risks

If `tpmi_sst_dev_add()` fails after core initialization, the probe explicitly calls `tpmi_sst_exit()`; mismatched usage counts would break later devices. All substantive behavior depends on the core's locking and package partition handling.

## Test Signals

Auxiliary device probe/remove, failure rollback, PM callback invocation, and module namespace imports validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.c

## Purpose

This file implements the hardware mapping and ioctl handling for Intel Speed Select Technology over TPMI. It hides package, partition, and power-domain layout details from userspace while exposing the same `/dev/isst_interface` UAPI used by older ISST transports.

## Important APIs, Types, And Functions

Core state types are `struct tpmi_per_power_domain_info`, `struct tpmi_sst_struct`, and `struct tpmi_sst_common_struct`. Discovery helpers include `sst_main()`, `sst_add_perf_profiles()`, `map_partition_power_domain_id()`, and `get_instance()`. Ioctl handlers cover core power (`isst_if_core_power_state()`), CLOS params/association, performance levels and feature state, level data, fabric data, CPU masks, base frequency, TPMI instance count, and turbo frequency. Public exported core functions are `tpmi_sst_init()`, `tpmi_sst_exit()`, `tpmi_sst_dev_add()`, `tpmi_sst_dev_remove()`, `tpmi_sst_dev_suspend()`, and `tpmi_sst_dev_resume()`.

## Control Flow

`tpmi_sst_init()` allocates the global package array and registers a TPMI backend default ioctl callback with the common ISST layer. `tpmi_sst_dev_add()` checks firmware read/write block status, gets OOB platform data, validates package and partition, maps each TPMI SST resource, parses SST/CP/PP headers, builds per-level offsets, and installs the partition into the package instance. `isst_if_def_ioctl()` serializes all TPMI ioctls under `isst_tpmi_dev_lock` and dispatches based on UAPI command. Removal clears the partition and frees the package instance when all partitions are gone. Suspend stores CP control, CLOS config/association, and PP control; resume writes them back.

## State And Persistence

Global state is `isst_common.sst_inst`, `isst_core_usage_count`, and package instances protected by `isst_tpmi_dev_lock`. Per-power-domain state includes mapped MMIO, header snapshots, level mappings, saved suspend values, write-block status, and device pointers. The driver preserves selected controls across suspend/resume but not reboot.

## Dependencies And Integration Points

The file depends on Intel TPMI resource APIs, Intel VSEC/OOB platform data, common ISST char-device registration, x86 HWP/MSR checks, topology package counts, and TPMI power-domain namespace imports. It translates UAPI structs from `uapi/linux/isst_if.h` into TPMI register reads/writes.

## Risks

Partition mapping is complex: if one partition is unbound, `map_partition_power_domain_id()` rejects all mappings because `partition_mask_current` no longer matches `partition_mask`. Several static local UAPI buffers are used in read handlers, but the global ioctl lock serializes access. Dynamic writes are blocked when HWP is unavailable or disabled. A likely bug exists in resume: the PP restore writes to `power_domain_info->sst_base` rather than `pd_info->sst_base`, which would restore all PP controls through the first element's base. Register-field macros must track TPMI spec revisions exactly.

## Test Signals

Tests should verify package/partition enumeration, instance count valid masks, invalid partition unbind behavior, all read-only info ioctls, CAP_SYS_ADMIN and write-block enforcement, dynamic feature rejection when HWP is off, level switching and retry behavior, CLOS association mapping, suspend/resume restore, and multi-resource systems with compute and IO dies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.h

## Purpose

This internal header declares the TPMI SST core entry points used by the auxiliary glue driver.

## Important APIs, Types, And Functions

It declares `tpmi_sst_init()`, `tpmi_sst_exit()`, `tpmi_sst_dev_add()`, `tpmi_sst_dev_remove()`, `tpmi_sst_dev_suspend()`, and `tpmi_sst_dev_resume()`.

## Control Flow

The glue driver calls init before adding the first auxiliary device, add/remove for each TPMI SST auxiliary device, suspend/resume from PM callbacks, and exit after removal.

## State And Persistence

No state is defined in the header; the implementation owns all state.

## Dependencies And Integration Points

The declarations require `struct auxiliary_device` from the auxiliary bus and connect `isst_tpmi.c` to `isst_tpmi_core.c`.

## Risks

The header has no include for `struct auxiliary_device`; it relies on including contexts or implicit forward visibility. Any signature changes must be coordinated with the glue driver and exported symbols.

## Test Signals

Compile/link of `isst_tpmi.o` with `isst_tpmi_core.o`, namespace exports, and probe/remove PM call paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Kconfig

## Purpose

This Kconfig option enables the legacy Intel SoC telemetry driver stack for Apollo Lake and later-style SoC telemetry.

## Important APIs, Types, And Functions

`INTEL_TELEMETRY` is a tristate depending on `X86_64`, `MFD_INTEL_PMC_BXT`, and `INTEL_PUNIT_IPC`.

## Control Flow

Enabling the option builds the telemetry core, platform driver, and debugfs interface from the directory Makefile.

## State And Persistence

No runtime state; it controls build selection.

## Dependencies And Integration Points

It ensures PMC and P-unit IPC dependencies are present because platform telemetry setup needs PMC MMIO/debug data and P-unit mailbox commands.

## Risks

The dependency set is narrow; builds without Apollo Lake/Goldmont-compatible runtime hardware still compile but probe should reject unsupported CPUs. Debugfs interfaces are included whenever the option is enabled.

## Test Signals

Kconfig dependency resolution, module build as `m`, built-in build as `y`, and absence of unresolved telemetry/P-unit/PMC symbols validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Makefile

## Purpose

This Makefile builds the three legacy Intel telemetry modules.

## Important APIs, Types, And Functions

It maps `intel_telemetry_core-y` to `core.o`, `intel_telemetry_pltdrv-y` to `pltdrv.o`, and `intel_telemetry_debugfs-y` to `debugfs.o`, all gated by `CONFIG_INTEL_TELEMETRY`.

## Control Flow

Kbuild compiles each module object when telemetry is enabled.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The split reflects API core, platform implementation, and debugfs presentation modules.

## Risks

The debugfs module depends on platform data being installed by the platform driver; load ordering matters at runtime even though all objects are selected by the same Kconfig.

## Test Signals

Build the option as module and built-in, inspect produced module names, and load modules in dependency order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/core.c

## Purpose

This file provides the legacy Intel SoC telemetry core API. It is a thin dispatcher from exported telemetry functions to platform-specific operations installed by `pltdrv.c`.

## Important APIs, Types, And Functions

`struct telemetry_core_config` holds current platform config and operation table. Exported APIs include `telemetry_read_events()`, `telemetry_read_eventlog()`, `telemetry_raw_read_eventlog()`, `telemetry_get_trace_verbosity()`, `telemetry_set_trace_verbosity()`, `telemetry_set_pltdata()`, `telemetry_clear_pltdata()`, `telemetry_get_pltdata()`, and `telemetry_get_evtname()`. Default operations return success without data until platform data is installed.

## Control Flow

Module init sets `telm_core_conf.telem_ops` to default no-op operations. The platform driver later calls `telemetry_set_pltdata()` with real operations and event maps. API callers then dispatch into those operations. `telemetry_get_evtname()` selects PSS or IOSS event name arrays from the platform config.

## State And Persistence

Global state is a single platform config pointer and ops pointer. There is no locking in core setters/getters; platform lifetime ordering is expected to prevent races. No persistent state exists.

## Dependencies And Integration Points

It depends on `asm/intel_telemetry.h` for UAPI-like telemetry structs and is consumed by platform, debugfs, and other in-kernel telemetry users.

## Risks

If callers use read APIs before platform data is set, default callbacks return 0, which can look like successful empty reads. There is no refcounting around `plt_config`, so debugfs must not outlive cleared platform data. Event-name access copies pointers from current config without synchronization.

## Test Signals

API calls before and after platform driver load, clear-on-remove behavior, PSS/IOSS event-name retrieval, and debugfs consumer behavior validate the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/debugfs.c

## Purpose

This file implements debugfs presentation for legacy Intel SoC telemetry. It renders PSS/IOSS event logs, SoC power-state summaries, S0ix residency, and trace verbosity controls under `/sys/kernel/debug/telemetry`.

## Important APIs, Types, And Functions

`struct telemetry_debugfs_conf` holds event IDs, bitfield decode tables, debugfs dentry, and accumulated suspend S0ix stats. Show functions are `telem_pss_states_show()`, `telem_ioss_states_show()`, and `telem_soc_states_show()`. Trace controls use `telem_pss_trc_verb_*` and `telem_ioss_trc_verb_*`. PM notifier helpers `pm_suspend_prep_cb()` and `pm_suspend_exit_cb()` accumulate suspend-only S0ix counters.

## Control Flow

Late init matches Goldmont/Goldmont Plus CPUs, verifies telemetry platform data exists, validates table sizes, registers a suspend notifier, creates the debugfs directory, and adds files. Reads call telemetry core APIs to fetch event logs, decode named bitfields, and format tables. `soc_states` also walks all PCI devices and reports D3 state from PMCSR. Suspend prepare snapshots S0ix counters with raw reads; post-suspend reads them again, corrects stale telemetry counters with PMC GCR if needed, and accumulates suspend stats.

## State And Persistence

Global state includes `debugfs_conf`, suspend temporary counters, and accumulated `suspend_stats`. Data is volatile and reset on module unload. Trace verbosity writes are persistent only in firmware until reset or later write.

## Dependencies And Integration Points

The file depends on telemetry core APIs, debugfs, seq_file, PCI enumeration, suspend notifiers, Intel PMC BXT helpers, and CPU model matching. It assumes `telemetry_get_pltdata()` is already populated.

## Risks

Several local arrays in show functions are not explicitly zeroed before parsing; if a matching event is absent, output can include uninitialized stack values. Debugfs init returns `-ENODEV` if platform telemetry has not initialized, so module load order matters. The debugfs file comments include a typo for `ioss_race_verbosity` but the actual file is `ioss_trace_verbosity`. PCI PMCSR reads assume `dev->pm_cap` is usable.

## Test Signals

Signals include debugfs file creation, event-log rendering with correct names, SoC state decoding, S0ix residency read, trace verbosity read/write, suspend notifier accumulation, behavior when platform data is missing, and KASAN/KMSAN coverage for absent event IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/pltdrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/pltdrv.c

## Purpose

This platform driver implements the hardware-specific legacy telemetry backend for Apollo Lake/Goldmont and Gemini Lake/Goldmont Plus. It configures default PSS and IOSS telemetry events through P-unit and SCU IPC and reads accumulated samples from SSRAM MMIO regions.

## Important APIs, Types, And Functions

Important objects are the default event maps, `telem_apl_config`, `telem_glk_config`, `telemetry_cpu_ids[]`, and platform ops `telm_pltops`. Setup functions include `telemetry_setup()`, `telemetry_setup_evtconfig()`, `telemetry_setup_iossevtconfig()`, and `telemetry_setup_pssevtconfig()`. Read functions include `telem_evtlog_read()`, `telemetry_plt_raw_read_eventlog()`, and `telemetry_plt_read_eventlog()`. Trace controls are `telemetry_plt_get_trace_verbosity()` and `telemetry_plt_set_trace_verbosity()`.

## Control Flow

Probe matches CPU model, selects platform config, obtains PMC parent data, maps PSS and IOSS SSRAM resources, obtains the SCU IPC device, initializes locks, queries telemetry capacity from IOSS and PSS firmware, programs default event maps with reset action, and installs platform ops into the telemetry core. Event setup disables telemetry, optionally clears or appends events, programs event IDs, then enables periodic SRAM tracing with the configured sample period. Reads use a timestamp-stability loop around SSRAM data to avoid torn samples.

## State And Persistence

Platform state is stored in the selected static `telemetry_plt_config`: event maps, event counts, periods, MMIO regmaps, IPC device, PMC pointer, locks, and `telem_in_use`. Firmware telemetry configuration persists in hardware until reset or reconfiguration; software state is volatile.

## Dependencies And Integration Points

The driver depends on P-unit IPC, SCU IPC, PMC BXT, platform MMIO resources, CPU matching, and telemetry core exported functions. Debugfs consumes the installed platform config and ops.

## Risks

Telemetry setup is all-or-nothing and depends on both IOSS and PSS firmware reporting at least 28 SRAM events/registers. `TELEM_MIN_PERIOD` and `TELEM_MAX_PERIOD` store masked rather than shifted values, so consumers must understand the encoding. Updating telemetry is rejected while `telem_in_use` is set. The timestamp loop returns `-EBUSY` if firmware updates too long. Event-map name strings are only initialized for defaults; update-added events can have IDs without meaningful names.

## Test Signals

Probe on supported CPUs, resource mapping, SCU/P-unit IPC command success, default PSS/IOSS event programming, stable SSRAM reads, trace verbosity get/set, telemetry core ops installation/clear, capacity failure behavior, and debugfs output using the configured event maps are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/pltdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.c

## Purpose

This module builds a mapping between Linux CPU numbers and Intel TPMI/P-unit power-domain identifiers using `MSR_PM_LOGICAL_ID`. Other TPMI-based drivers use it to translate package/domain/core IDs and obtain power-domain CPU masks.

## Important APIs, Types, And Functions

`struct tpmi_cpu_info` stores Linux CPU, package, P-unit thread/core/domain IDs, and a hash node. Exported APIs are `tpmi_get_linux_cpu_number()`, `tpmi_get_punit_core_number()`, `tpmi_get_power_domain_id()`, `tpmi_get_power_domain_mask()`, and `tpmi_get_linux_die_id()`. `tpmi_cpu_online()` populates per-CPU info, per-domain cpumasks, hash entries, and domain-to-die mapping.

## Control Flow

Module init matches supported Intel models, verifies MSR `0x54`, allocates `topology_max_packages() * MAX_POWER_DOMAINS` masks and die-map entries, then installs a dynamic CPU hotplug online callback. Each online CPU reads the logical ID MSR, decodes LP/module/domain fields, and records mapping data under `tpmi_lock`. Exit removes the hotplug state and frees arrays.

## State And Persistence

State includes per-CPU `tpmi_cpu_info`, a global hash keyed by P-unit core ID, per-package/domain cpumasks, and a package/domain die map. It is volatile kernel memory.

## Dependencies And Integration Points

The module depends on x86 CPU model matching, cpuhotplug, topology APIs, MSR access, cpumasks, and exports namespace `INTEL_TPMI_POWER_DOMAIN`, imported by TPMI SST and related drivers.

## Risks

There is no CPU offline callback to clear masks/hash entries, so CPU hot-unplug could leave stale mappings. `tpmi_get_power_domain_mask()` returns a pointer after dropping the mutex guard, so callers see shared mutable masks. Hash lookup by core ID also filters package/domain, but duplicate core IDs within a domain would return the first online CPU. Domain count is fixed at 8.

## Test Signals

CPU model matching, MSR decode correctness, CPU hotplug online population, exported lookup functions for all online CPUs, multi-package/domain masks, invalid CPU/package/domain rejection, and hot-unplug behavior should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.h

## Purpose

This header declares the exported TPMI power-domain mapping helpers.

## Important APIs, Types, And Functions

It declares CPU/domain translation helpers: `tpmi_get_linux_cpu_number()`, `tpmi_get_punit_core_number()`, `tpmi_get_power_domain_id()`, `tpmi_get_power_domain_mask()`, and `tpmi_get_linux_die_id()`.

## Control Flow

Consumers call these helpers after the mapping module initializes and CPU online callbacks populate state.

## State And Persistence

No state is defined here; implementation state is in `tpmi_power_domains.c`.

## Dependencies And Integration Points

It includes `linux/cpumask.h` because one helper returns `cpumask_t *`. It is used by TPMI feature drivers that need P-unit domain to Linux topology translation.

## Risks

The prototype names the second argument of `tpmi_get_linux_cpu_number()` as `die_id`, while the implementation treats it as `domain_id`; this naming mismatch can confuse consumers.

## Test Signals

Compile consumers, namespace import/export checks, and semantic tests for package/domain/core lookups validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/turbo_max_3.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/turbo_max_3.c

## Purpose

This legacy Intel Turbo Boost Max Technology 3.0 driver discovers per-core favored-core priority on non-HWP Broadwell-X and Skylake-X systems and feeds the scheduler's ITMT priority mechanism.

## Important APIs, Types, And Functions

`get_oc_core_priority()` issues an overclocking mailbox favored-core read through `MSR_OC_MAILBOX`. `itmt_legacy_cpu_online()` reads each CPU's priority, calls `sched_set_itmt_core_prio()`, and schedules work to enable ITMT once distinct priorities are seen. `itmt_legacy_work_fn()` calls `sched_set_itmt_support()` outside CPU hotplug locking.

## Control Flow

`late_initcall()` matches Broadwell-X or Skylake-X and installs a dynamic CPU hotplug online callback. Each online CPU queries mailbox priority. The first time observed max priority exceeds min priority, deferred work enables scheduler ITMT support.

## State And Persistence

Static local `max_highest_perf` and `min_highest_perf` track observed priority spread. Scheduler priority state persists in scheduler data until CPU teardown or reboot. No module exit path is present because this is initcall-style built-in behavior.

## Dependencies And Integration Points

The driver depends on x86 MSR access, CPU model matching, CPU hotplug, topology/scheduler ITMT APIs, and workqueues.

## Risks

Mailbox retries are minimal; transient busy status can skip a CPU priority. Static min/max are not protected by a lock, relying on CPU hotplug serialization. No cpuhp state is removed because there is no exit. It targets only legacy non-HWP platforms.

## Test Signals

Supported CPU match, MSR mailbox success/failure logs, scheduler priority values per CPU, ITMT support enabled only after nonuniform priorities, and CPU online hotplug behavior are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/turbo_max_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Kconfig

## Purpose

This Kconfig fragment defines Intel uncore frequency control driver options.

## Important APIs, Types, And Functions

`INTEL_UNCORE_FREQ_CONTROL` is the user-visible tristate and selects `INTEL_UNCORE_FREQ_CONTROL_TPMI` when `INTEL_TPMI` is enabled. The menu depends on `X86_64 || COMPILE_TEST`.

## Control Flow

Enabling the option builds the legacy/main uncore frequency module, common sysfs module, and TPMI backend when available.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The option integrates with platform/x86 Intel uncore frequency sysfs and TPMI backend support.

## Risks

The prompt has a spelling typo in "Frquency". TPMI backend inclusion depends on `INTEL_TPMI`; unsupported systems rely on runtime probe checks.

## Test Signals

Kconfig selection with and without TPMI, module builds, and dependency-free COMPILE_TEST builds are expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Makefile

## Purpose

This Makefile builds Intel uncore frequency control objects.

## Important APIs, Types, And Functions

`CONFIG_INTEL_UNCORE_FREQ_CONTROL` builds `intel-uncore-frequency.o` from `uncore-frequency.o` and `intel-uncore-frequency-common.o` from `uncore-frequency-common.o`. `CONFIG_INTEL_UNCORE_FREQ_CONTROL_TPMI` builds `intel-uncore-frequency-tpmi.o`.

## Control Flow

Kbuild compiles selected objects according to Kconfig.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

It separates the common sysfs layer, original backend, and TPMI backend.

## Risks

Runtime module ordering must ensure the common module's exported namespace is available to backends.

## Test Signals

Builds with base-only and TPMI configurations, module dependency resolution, and namespace import/export checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.c

## Purpose

This file implements the shared sysfs layer for Intel uncore frequency control. Hardware-specific backends provide read/write callbacks and per-instance `struct uncore_data`; the common layer creates and removes sysfs groups under the CPU subsystem.

## Important APIs, Types, And Functions

Exports are `uncore_freq_common_init()`, `uncore_freq_common_exit()`, `uncore_freq_add_entry()`, and `uncore_freq_remove_die_entry()`. Internal helpers generate show/store callbacks for min/max/current frequency, initial values, ELC thresholds, domain/cluster/package IDs, agent types, and die ID. `create_attr_group()` dynamically includes optional attributes only when backend reads succeed or metadata is meaningful.

## Control Flow

A backend calls `uncore_freq_common_init()` with hardware read/write callbacks; the common layer creates `/sys/devices/system/cpu/intel_uncore_frequency` once and increments an instance count. For each die/domain, the backend calls `uncore_freq_add_entry()`, which names the instance, samples initial min/max frequencies, creates attributes, and marks the entry valid. Writes parse integers or booleans, serialize under `uncore_lock`, and call the backend write callback. Removal deletes the group, clears validity, and frees any allocated IDA instance. Exit drops the root kobject when the last backend exits.

## State And Persistence

Global state includes `uncore_lock`, root kobject, instance count, IDA allocator, and callback pointers. Per-instance state lives in backend-owned `struct uncore_data`, including cached initial frequency values and validity/control CPU. User writes modify hardware state; common code stores no resume policy beyond the `stored_uncore_data` field available to backends.

## Dependencies And Integration Points

The file integrates with the CPU subsystem root device, sysfs/kobject APIs, IDA, topology helpers, and hardware-specific uncore backends. It exports namespace `INTEL_UNCORE_FREQUENCY`.

## Risks

Only one global read/write callback pair exists, so simultaneous different backend types would conflict. `uncore_freq_remove_die_entry()` assumes the entry is valid and group exists. `kstrtobool(buf, (bool *)&input)` writes through a bool pointer into an unsigned int object, which is unusual and depends on layout. Attribute array capacity must stay in sync with optional attributes.

## Test Signals

Signals include root kobject creation/removal, sysfs group creation for package/die and domain modes, optional current/ELC attributes appearing only when reads succeed, min/max writes reaching backend callbacks, boolean ELC parsing, IDA naming, and concurrent access serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.h

## Purpose

This header defines the common data model and callback contract for Intel uncore frequency control backends.

## Important APIs, Types, And Functions

It defines agent type bitmasks, `struct uncore_data`, `UNCORE_DOMAIN_ID_INVALID`, `enum uncore_index`, and prototypes for common init/exit and entry add/remove functions. `struct uncore_data` contains hardware metadata, cached initial frequencies, control CPU, sysfs attribute storage, and an attribute pointer array.

## Control Flow

Backends allocate/fill `struct uncore_data`, initialize common callbacks, add entries when control CPUs/devices are available, and remove entries during teardown or CPU/device removal.

## State And Persistence

The header defines fields used for runtime state but owns none itself. `stored_uncore_data` is reserved for backend resume restoration.

## Dependencies And Integration Points

It includes Linux device/sysfs types and is shared by the common module plus uncore frequency backends.

## Risks

`uncore_attrs[15]` must be large enough for all optional attributes; adding fields in common code requires increasing this bound. Backends must keep `control_cpu`, package/die/domain IDs, and agent masks consistent with hardware.

## Test Signals

Compile backends, sysfs attribute count coverage, domain and package mode entries, and backend read/write callback invocation for every `enum uncore_index` validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.h -->
