# Research: subset-b-005192

This grouped report covers the exact source files assigned to `subset-b-005192`. Each section is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_r5_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_r5_remoteproc.c

## Purpose

This file implements the Linux remoteproc platform driver for TI K3 R5F clusters. It binds R5F subsystem device-tree nodes such as `ti,am654-r5fss`, `ti,j7200-r5fss`, `ti,am64-r5fss`, `ti,am62-r5fss`, and `ti,j721s2-r5fss`, constructs one or more `struct rproc` instances, and controls reset, halt/run, boot vectors, TCM layout, reserved memory, SRAM, and mailbox integration for firmware running on the R5 cores.

The driver supports split mode, lockstep mode, AM64x single-CPU mode, and AM62x single-core mode. It also has IPC-only attach support when a bootloader has already loaded and started firmware before Linux probes the device.

## Important APIs, Types, And Functions

Key local types are `enum cluster_mode`, `struct k3_r5_soc_data`, `struct k3_r5_cluster`, and `struct k3_r5_core`. `k3_r5_soc_data` carries SoC differences such as doubled TCM windows, TCM ECC auto-init, single-CPU support, and single-core IP. `k3_r5_cluster` owns cluster mode, the list of `k3_r5_core` children, and a wait queue used to enforce core sequencing. `k3_r5_core` stores child device state, its `struct k3_rproc`, SRAM descriptors, TCM configuration bits, and `released_from_reset`.

Remoteproc operations are exported through `k3_r5_rproc_ops`: `.prepare`, `.unprepare`, `.start`, `.stop`, `.kick`, and `.da_to_va`. Preparation and unpreparation release or assert resets so firmware can be loaded into TCMs. Start and stop program the boot vector and clear or set the TI-SCI halt bit. Address translation first checks optional SRAM regions and then delegates to the shared K3 remoteproc translation helper.

Reset and power helpers split into `k3_r5_split_reset()`, `k3_r5_split_release()`, `k3_r5_lockstep_reset()`, and `k3_r5_lockstep_release()`. Processor control uses `ti_sci_proc_get_status()`, `ti_sci_proc_set_config()`, and `ti_sci_proc_set_control()` from `ti_sci_proc.h`, plus TI-SCI device `get_device` and `put_device` operations.

Probe and initialization flow is anchored by `k3_r5_probe()`, `k3_r5_cluster_of_init()`, `k3_r5_core_of_init()`, and `k3_r5_cluster_rproc_init()`. Static match data maps compatibles to SoC capabilities and the common `r5_data` memory layout for ATCM and BTCM.

## Control Flow

`k3_r5_probe()` allocates the cluster object, reads `ti,cluster-mode` or chooses a SoC-specific default, validates the number of child cores, populates child platform devices, parses per-core DT properties, and initializes remoteproc objects. Per-core init defaults to ATCM disabled, BTCM enabled, and `loczrama` true unless `ti,atcm-enable`, `ti,btcm-enable`, or `ti,loczrama` override those settings. Optional `sram` phandles are converted to memory mappings.

`k3_r5_cluster_rproc_init()` walks each child core, parses firmware name, allocates a `rproc`, obtains TI-SCI and reset handles, creates a `ti_sci_proc` helper from `ti,sci-proc-ids`, maps internal memories, requests processor ownership, and later requests mailboxes, detects remoteproc versus IPC-only mode, configures TI-SCI boot flags, initializes reserved memory, and registers the `rproc`. In lockstep, single-CPU, and single-core modes only one remoteproc is registered.

Booting through remoteproc calls `.prepare`, `.start`, `.stop`, and `.unprepare`. Split mode enforces power-up order, waiting up to two seconds for core0 before core1, and power-down order, waiting for core1 before core0. Lockstep start programs core0 boot configuration and unhalts cores in reverse order; stop halts core0 then core1. Single-CPU mode reuses lockstep reset release/assert for combined TCM access but only runs core0.

IPC-only detection in `k3_r5_rproc_configure_mode()` queries TI-SCI device power, local reset status, and halt control. If the module is powered, local reset is deasserted, and the core is unhalted, the rproc is marked `RPROC_DETACHED` and its operations are reduced to attach/detach/resource-table support.

## State And Persistence

Runtime state is in devm-managed cluster/core structures and remoteproc private data. `released_from_reset` is the key local sequencing flag, protected by ordering through remoteproc callbacks and signaled via `cluster->core_transition`. Firmware-visible state is persistent in System Firmware controlled boot configuration bits: lockstep, single-core, ATCM/BTCM enable, TCM reset base, TEINIT, halt/run control, and boot vector. The driver also updates TCM device addresses when IPC-only mode reveals actual bootloader settings.

Memory mappings for ATCM/BTCM, SRAM, and reserved memory are held for the lifetime of the device. `k3_reserved_mem_init()` integrates carveouts with remoteproc. Cleanup is devm-action based: `k3_r5_cluster_of_exit()` drops child core resources and `k3_r5_cluster_rproc_exit()` detaches attached remoteprocs in a mode-aware order.

## Dependencies And Integration Points

The driver depends on the remoteproc core, TI-SCI protocol, TI K3 common remoteproc helpers, reset framework, OMAP/K3 mailbox support, devicetree child devices, reserved-memory bindings, and SoC match data. It includes `omap_remoteproc.h`, `remoteproc_internal.h`, `ti_sci_proc.h`, and `ti_k3_common.h`.

Important DT properties are `ti,cluster-mode`, `firmware-name`, `ti,sci`, `ti,sci-dev-id`, `ti,sci-proc-ids`, `ti,atcm-enable`, `ti,btcm-enable`, `ti,loczrama`, and optional `sram` phandles. Integration with rpmsg happens indirectly through remoteproc and mailbox kick support.

## Risks And Edge Cases

The source contains visible duplicate lines and an apparently stray extra closing brace after `k3_r5_cluster_rproc_exit()`, which is a source-integrity risk in this tree. Functionally, boot address sanity checking is explicitly marked TODO, so invalid firmware entry points are not rejected here. Split-mode sequencing relies on a two-second timeout and shared `released_from_reset` state, which can fail if remoteproc requests are concurrent or core0 is not progressing. IPC-only mode is strict: mismatched power, local reset, or halt state returns `-EINVAL`.

TCM address modeling is simplified: comments note that R5 region registers can place ATCM/BTCM elsewhere, but the driver currently assigns only address 0 and `0x41010000` based on `loczrama`. Lockstep configuration works around System Firmware limitations by temporarily programming both cores symmetrically, so TI-SCI NACK behavior and eFUSE status bits are important failure points. Error recovery is disabled for remoteproc instances.

## Test Signals

There is no direct KUnit coverage in this file. Test signals are platform probe success, remoteproc sysfs lifecycle behavior, IPC-only attach/detach behavior, TI-SCI status/config/control results, correct reserved-memory and TCM loading, mailbox/rpmsg operation, and DT validation for supported SoCs and modes. The duplicated/extra-brace source signals should also be caught by compile testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_r5_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_sci_proc.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_sci_proc.h

## Purpose

This header provides small inline helper wrappers around the TI-SCI processor control protocol for remoteproc drivers. It packages the TI-SCI handle, processor operation table, owning device, processor ID, and handover host ID into `struct ti_sci_proc`, then exposes request, release, handover, configuration, control, and status calls with consistent device-scoped error logging.

## Important APIs, Types, And Functions

`struct ti_sci_proc` stores `sci`, `ops`, `dev`, `proc_id`, and `host_id`. `ti_sci_proc_of_get_tsp()` reads the two-value `ti,sci-proc-ids` device-tree property, allocates the helper with `devm_kzalloc()`, and binds it to `sci->ops.proc_ops`. The remaining inline functions directly wrap TI-SCI processor ops: `request`, `release`, `handover`, `set_config`, `set_control`, and `get_status`.

`ti_sci_proc_set_config()` takes a boot vector and bit masks to set and clear processor configuration flags. `ti_sci_proc_set_control()` changes runtime control flags such as halt/run. `ti_sci_proc_get_status()` returns boot vector, config flags, control flags, and status flags.

## Control Flow

A remoteproc driver first obtains a TI-SCI handle, calls `ti_sci_proc_of_get_tsp()`, and then uses the returned helper through the remote processor lifecycle. The wrappers do no policy work; they forward parameters to firmware and return firmware errors unchanged after logging.

## State And Persistence

The helper object is devm-managed and persists for the owning device lifetime. Hardware and firmware state is not stored in the helper beyond IDs; persistent processor state lives in System Firmware and is read or modified through TI-SCI.

## Dependencies And Integration Points

The header depends on `<linux/soc/ti/ti_sci_protocol.h>` and a DT binding that supplies `ti,sci-proc-ids`. It is used by TI remoteproc drivers such as the K3 R5 driver to avoid open-coded TI-SCI processor operations.

## Risks And Edge Cases

The helper assumes a valid non-NULL TI-SCI handle and proc ops table. A missing or malformed `ti,sci-proc-ids` property returns an error pointer, and all wrappers assume the caller has already checked it. There is no internal serialization; callers must sequence firmware operations correctly.

## Test Signals

Coverage is indirect through remoteproc drivers that request and configure TI-SCI controlled processors. Useful tests include missing property probe failure, request/release error propagation, and boot/control/status sequencing on real or mocked TI-SCI firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_sci_proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/wkup_m3_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/wkup_m3_rproc.c

## Purpose

This file implements the remoteproc driver for the TI AM335x/AM437x Wakeup M3 processor. The Wakeup M3 is a small firmware-controlled power-management processor; this driver exposes it to the remoteproc framework, maps its UMEM/DMEM regions for firmware loading, and controls reset through either a reset-controller handle or legacy platform data callbacks.

## Important APIs, Types, And Functions

`struct wkup_m3_mem` records CPU virtual address, bus address, M3 device address, and size for each internal memory region. `struct wkup_m3_rproc` stores the `rproc`, platform device, two memory descriptors, and optional reset control.

The remoteproc ops are `wkup_m3_rproc_start()`, `wkup_m3_rproc_stop()`, and `wkup_m3_rproc_da_to_va()`. Start deasserts reset; stop asserts reset. If no reset controller is present, legacy `wkup_m3_platform_data` callbacks provide reset operations. `wkup_m3_rproc_da_to_va()` translates firmware device addresses into mapped UMEM/DMEM kernel addresses.

`wkup_m3_rproc_probe()` performs all setup: reads `ti,pm-firmware`, enables runtime PM, allocates the remoteproc, gets reset control or platform callbacks, maps named memory resources `umem` and `dmem`, computes M3-relative device addresses, and registers the remoteproc.

## Control Flow

Probe requires a firmware filename from device tree. Runtime PM is enabled and a `devm_add_action_or_reset()` callback balances the initial `pm_runtime_get_sync()`. The remoteproc is allocated with `auto_boot = false` and `sysfs_read_only = true`, so firmware is not automatically started and sysfs users cannot mutate normal remoteproc state. Memory mapping processes `umem` first, because the M3 address space treats UMEM as device address zero; each region's device address is then normalized by subtracting UMEM's bus offset.

At remoteproc start, reset is deasserted through the reset framework or platform callback. Stop mirrors this with reset assertion. Address translation scans both internal memories and returns NULL for zero-length or out-of-range requests.

## State And Persistence

Driver state is devm-managed under the platform device. The memory map persists while the device is bound. The M3 firmware lifecycle is explicitly non-autoboot, and the driver keeps runtime PM active for its lifetime by refusing runtime suspend with `-EBUSY`.

## Dependencies And Integration Points

The driver integrates with remoteproc, runtime PM, reset framework, devicetree resources, and legacy `linux/platform_data/wkup_m3.h`. It binds `ti,am3352-wkup-m3` and `ti,am4372-wkup-m3`. Required resource names are `umem` and `dmem`, and required DT firmware property is `ti,pm-firmware`.

## Risks And Edge Cases

The fallback path requires complete platform data if the reset controller is absent; otherwise probe fails. `of_get_address()` results are dereferenced without an explicit NULL check after resource mapping, so malformed DT address data could be risky. Runtime suspend always returns busy, which is intentional for availability but prevents deeper PM states for this device. The driver has no crash recovery or mailbox handling of its own.

## Test Signals

Probe tests should cover firmware property absence, reset-controller and platform-data reset paths, resource mapping for both memories, and address translation boundaries. Runtime tests should verify start/stop reset polarity and that PM runtime references are balanced on probe failure and device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/wkup_m3_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/xlnx_r5_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/xlnx_r5_remoteproc.c

## Purpose

This file implements the Xilinx/ZynqMP, Versal, and Versal Net R5/R52 remoteproc platform driver. It builds remoteproc instances for RPU child cores, configures cluster mode and TCM layout through Xilinx platform-management firmware, maps TCM/SRAM/reserved-memory carveouts, handles IPI mailbox kicks, and supports both normal firmware boot and attach to firmware already running in memory.

## Important APIs, Types, And Functions

Primary data structures are `struct mem_bank_data`, `struct zynqmp_sram_bank`, `struct mbox_info`, `struct rsc_tbl_data`, `struct zynqmp_r5_core`, and `struct zynqmp_r5_cluster`. The cluster stores mode and child core pointers. Each core stores TCM bank descriptors, SRAM banks, PM domain ID, remoteproc handle, optional mailbox information, and loaded resource-table metadata.

The remoteproc operations in `zynqmp_r5_rproc_ops` include prepare/unprepare, start/stop, ELF load and sanity operations, firmware resource-table parsing, mailbox kick, attach/detach, and loaded resource table access. `zynqmp_r5_rproc_start()` uses `zynqmp_pm_request_node()` and `zynqmp_pm_request_wake()` with a boot memory selector derived from the boot address. `zynqmp_r5_rproc_stop()` uses `PM_RELEASE_NODE` when available or falls back to `PM_FORCE_POWERDOWN`.

Memory setup is split across `add_tcm_banks()`, `add_mem_regions_carveout()`, and `add_sram_carveouts()`. TCM information can come from DT `reg` plus power domains via `zynqmp_r5_get_tcm_node_from_dt()`, or from legacy hardcoded ZynqMP TCM tables via `zynqmp_r5_get_tcm_node()`.

Mailbox setup uses `zynqmp_r5_setup_mbox()`, `zynqmp_r5_mb_rx_cb()`, `handle_event_notified()`, and `zynqmp_r5_rproc_kick()`. RX acknowledges the mailbox and schedules work that scans all remoteproc notify IDs.

## Control Flow

`zynqmp_r5_remoteproc_probe()` allocates a cluster, populates child platform devices, sets driver data, initializes cluster/core state, and registers cleanup. `zynqmp_r5_cluster_init()` reads `xlnx,cluster-mode`, accepts split or lockstep mode, determines TCM mode, validates child core count, allocates child device and core arrays, creates remoteproc instances, optionally sets up mailboxes, and initializes hardware mode through platform-management firmware.

`zynqmp_r5_add_rproc_core()` allocates a remoteproc, disables recovery and IOMMU, sets `auto_boot = false`, registers with remoteproc, and then tries to locate a preloaded resource table. If the magic-bearing metadata in the first `memory-region` entry is valid, the rproc state becomes `RPROC_DETACHED`.

Prepare powers on TCM banks and registers carveouts unless already detached, then adds reserved-memory and SRAM carveouts. Start requests and wakes the core from low or high vectors. Stop releases or powers down the PM node. Unprepare releases all TCM power-domain nodes. Shutdown handles kexec by shutting down running rprocs or detaching attached ones.

## State And Persistence

Per-core state persists until cluster cleanup. TCM banks are requested during prepare and released during unprepare. The resource table VA and size persist for detached attach mode after metadata validation. Mailbox channels are manually allocated and freed, not devm-managed. Platform firmware owns durable RPU mode, TCM configuration, wake, node request, and power-down state.

## Dependencies And Integration Points

The driver depends on remoteproc, reserved memory, mailbox framework, Xilinx IPI message formats, Xilinx firmware PM APIs, device tree child nodes, power-domain bindings, and PM domain IDs such as `PD_R5_0_ATCM`. It binds `xlnx,versal-net-r52fss`, `xlnx,versal-r5fss`, and `xlnx,zynqmp-r5fss`.

Important DT inputs include `xlnx,cluster-mode`, `xlnx,tcm-mode`, child `power-domains`, optional child `reg` TCM resources, `memory-region`, optional `sram`, and optional `mboxes`/`mbox-names`.

## Risks And Edge Cases

The source in this tree contains duplicated declarations and duplicated comments, including a duplicate `enum rpu_tcm_comb tcm_mode;`, which is a compile-integrity risk. `zynqmp_r5_get_rsc_table_va()` returns early on invalid magic without unmapping `rsc_data_va`, so the error path appears to leak an ioremap. Mailbox support is optional and failure only warns, so IPC may silently run without kicks if DT is incomplete. Lockstep mode with two enabled child nodes ignores the second node. Hardcoded legacy TCM tables are retained for old ZynqMP DTs and can diverge from actual hardware if bindings are wrong.

The driver disables recovery, so remote firmware faults are not automatically recovered. Resource-table attach depends on the first memory-region containing a packed metadata structure with exact magic and complement values.

## Test Signals

Test signals include probe under split and lockstep DTs, PM firmware calls for RPU and TCM modes, remoteproc boot and stop, TCM/SRAM/reserved-memory carveout registration, IPI kick and RX notification behavior, detached attach with valid and invalid resource-table metadata, and shutdown behavior during kexec. Compile testing should catch the duplicated declaration in this source snapshot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/xlnx_r5_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/resctrl/Kconfig

## Purpose

This Kconfig fragment defines build-time configuration for the Arm MPAM driver and its optional resctrl filesystem bridge. It gates the MPAM MSC discovery/control code, debug logging, KUnit tests, and automatic resctrl integration.

## Important APIs, Types, And Functions

`menuconfig ARM64_MPAM_DRIVER` enables the MPAM driver on `ARM64 && ARM64_MPAM` and selects `ACPI_MPAM` when ACPI is enabled. `ARM64_MPAM_DRIVER_DEBUG` adds debug messages. `MPAM_KUNIT_TEST` enables MPAM KUnit tests when KUnit is built in, defaulting to `KUNIT_ALL_TESTS`. `ARM64_MPAM_RESCTRL_FS` is a hidden bool defaulting to yes when both `ARM64_MPAM_DRIVER` and `RESCTRL_FS` are enabled; it selects `RESCTRL_RMID_DEPENDS_ON_CLOSID` and `RESCTRL_ASSIGN_FIXED`.

## Control Flow

The configuration flow is compile-time only. Enabling the main driver opens the nested debug and test options. If resctrl is present, the hidden bridge option automatically includes `mpam_resctrl.o` through the Makefile.

## State And Persistence

There is no runtime state in this file. It determines which objects, debug flags, and resctrl capabilities are compiled into the kernel.

## Dependencies And Integration Points

The fragment integrates Arm64 architectural MPAM support, ACPI MPAM discovery, Linux resctrl, and KUnit. The selected resctrl flags are important because MPAM RMID identity depends on both CLOSID/PARTID and PMG, and because monitor assignment is fixed rather than dynamically assigned like some x86 features.

## Risks And Edge Cases

`ARM64_MPAM_RESCTRL_FS` is hidden and automatic, so enabling `RESCTRL_FS` with MPAM compiles the bridge even if a platform has limited MPAM features. `MPAM_KUNIT_TEST` requires `KUNIT=y`, not module KUnit. Debug logging is compile-time through `-DDEBUG`.

## Test Signals

Build matrix signals are main driver on/off, ACPI on/off selection, debug flag compilation, KUnit inclusion, and resctrl bridge inclusion only when both MPAM driver and resctrl are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/resctrl/Makefile

## Purpose

This Makefile defines how the MPAM driver objects are built under `drivers/resctrl`. It creates a composite `mpam.o` object from the device layer and optionally the resctrl bridge.

## Important APIs, Types, And Functions

`obj-$(CONFIG_ARM64_MPAM_DRIVER) += mpam.o` builds the composite driver when the main Kconfig option is enabled. `mpam-y += mpam_devices.o` always includes the MSC/device layer. `mpam-$(CONFIG_ARM64_MPAM_RESCTRL_FS) += mpam_resctrl.o` conditionally includes the resctrl filesystem integration. `ccflags-$(CONFIG_ARM64_MPAM_DRIVER_DEBUG) += -DDEBUG` enables `pr_debug()` output for the driver.

## Control Flow

The build flow is Kbuild-controlled. Kconfig selects decide whether `mpam.o` exists, whether `mpam_resctrl.o` is linked into it, and whether debug macro behavior changes at compile time.

## State And Persistence

There is no runtime state. This file controls object composition and compile flags.

## Dependencies And Integration Points

It depends on the symbols defined by `Kconfig` in the same directory. The composite object links the public functions shared between `mpam_devices.c` and `mpam_resctrl.c` through `mpam_internal.h`.

## Risks And Edge Cases

Because `test_mpam_devices.c` is included from `mpam_devices.c` under KUnit rather than listed here, test compilation depends on C preprocessor inclusion and Kconfig rather than Makefile test objects. Debug behavior is broad for all objects compiled under this directory when the debug option is set.

## Test Signals

Build tests should verify object inclusion for `CONFIG_ARM64_MPAM_DRIVER=y`, optional `CONFIG_ARM64_MPAM_RESCTRL_FS`, and `CONFIG_ARM64_MPAM_DRIVER_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_devices.c -->
# sources/distributed-fs/ceph-client/drivers/resctrl/mpam_devices.c

## Purpose

This file is the core Arm MPAM Memory System Component driver. It discovers MPAM MSC hardware from ACPI/platform devices, builds the internal MSC/RIS/vMSC/component/class topology, probes hardware features, merges feature sets into usable classes, manages global PARTID/PMG limits, programs partition and monitor registers, handles CPU hotplug, exposes configuration and monitoring helpers to the resctrl bridge, and disables/reset MPAM on hardware error interrupts.

## Important APIs, Types, And Functions

Exported or cross-file APIs include `mpam_register_requestor()`, `mpam_ris_create()`, `mpam_enable()`, `mpam_disable()`, `mpam_reset_class_locked()`, `mpam_apply_config()`, `mpam_msmon_read()`, `mpam_msmon_reset_mbwu()`, and `mpam_get_cpumask_from_cache_id()`.

The file owns global structures declared in `mpam_internal.h`: `mpam_srcu`, `mpam_classes`, `mpam_partid_max`, and `mpam_pmg_max`. Local state includes `mpam_all_msc`, `mpam_num_msc`, `mpam_cpuhp_state`, `partid_max_init`, `partid_max_published`, work items for enable/disable, `mpam_disable_reason`, and a garbage list for deferred SRCU-safe freeing.

Feature probing reads MPAM registers through helpers such as `mpam_msc_read_idr()`, `mpam_ris_hw_probe()`, and `mpam_msc_hw_probe()`. Configuration programming is centered on `mpam_reprogram_ris_partid()`, `mpam_reprogram_msc()`, `mpam_reset_ris()`, and `mpam_apply_config()`. Monitoring is centered on `mpam_msmon_read()`, `__ris_msmon_read()`, MBWU save/restore helpers, and CSU/MBWU counter setup helpers.

## Control Flow

The init path begins at `subsys_initcall(mpam_msc_driver_init)`. It checks architectural MPAM support, initializes SRCU, counts firmware-described MSCs through ACPI, and registers a platform driver named `mpam_msc`. Each platform probe allocates and maps an `mpam_msc`, initializes locks, determines CPU accessibility, sets up optional error IRQ metadata, maps MMIO, adds the MSC to `mpam_all_msc`, and asks ACPI MPAM parsing to create RIS topology entries.

Once the number of probed MSC devices matches firmware count, CPU hotplug callbacks are registered in discovery mode. As CPUs come online, `mpam_discovery_cpu_online()` probes MSCs accessible from that CPU. When all MSCs are probed, `mpam_enable_work` runs `mpam_enable_once()`: it publishes fixed PARTID/PMG limits, merges vMSC/component/class features, registers error IRQs, allocates per-component configuration arrays and monitor state, initializes resctrl if enabled, turns on the `mpam_enabled` static branch, and swaps CPU hotplug callbacks to online/offline runtime handlers.

Runtime CPU online callbacks re-enable PPIs if needed and reprogram MSCs on first online reference. CPU offline callbacks reset RIS state and save MBWU monitor state before the last accessible CPU goes offline. Configuration writes update the per-component config array and call into the target MSC via `smp_call_on_cpu()` on an accessible CPU.

## State And Persistence

The MPAM topology is a graph: MSCs contain RIS; RIS belong to vMSCs; vMSCs belong to components; components belong to classes. Lists are protected by `mpam_list_lock` for writes and SRCU for readers. Objects removed from SRCU lists are added to `mpam_garbage` and freed after `synchronize_srcu()`.

System-wide `mpam_partid_max` and `mpam_pmg_max` are reduced to the smallest safe values across requestors and MSCs. Once `partid_max_published` is set, later requestors cannot lower the limits. Each component owns an array of `struct mpam_config` indexed by PARTID; reset defaults fill CPBM/MBW bitmap/max values according to class capabilities. MBWU monitor correction and configuration state are preserved across power management with per-RIS `msmon_mbwu_state` arrays.

Hardware state is persistent in MSC MMIO registers until reset or reprogramming. `mpam_disable()` clears the static branch, removes CPU hotplug callbacks, exits resctrl, unregisters interrupts, resets classes to default controls, tears down class usage, destroys MSC topology, and frees deferred objects.

## Dependencies And Integration Points

The driver depends on Arm MPAM architectural support, ACPI MPAM firmware discovery, platform devices named `mpam_msc`, cache/PPTT topology, CPU hotplug, SRCU, workqueues, interrupts, cpumasks, and optional resctrl hooks. It currently supports MMIO MSCs; PCC-backed MSCs are detected but rejected.

It integrates with vendor errata handling for NVIDIA T241 and ARM CMN-650. T241 quirks map scratch registers, force MBW minimum behavior, scale bandwidth counters, and scrub shadow registers after config changes. Error IRQs may be SPI or PPI and are treated as fatal software-bug indicators.

## Risks And Edge Cases

The source contains visible duplicated lines in this snapshot, including duplicated condition lines and duplicated `return err;`, which is a source-integrity risk. Monitoring currently has a TODO for scaling counters. Locking is complex: `mpam_list_lock`, per-MSC `probe_lock`, `part_sel_lock`, `cfg_lock`, raw monitor selector lock, CPU hotplug locks, and SRCU all have ordering expectations. Incorrect access CPU selection can hit powered-off private MSCs; the code mitigates this by selecting CPUs from each MSC accessibility mask.

Feature merging intentionally drops or narrows capabilities when resources do not alias or have incompatible widths. That avoids unsafe programming but can hide hardware features from resctrl. Any MPAM hardware error interrupt disables the entire driver and tears down resctrl. PCC interfaces are not implemented. Malformed firmware topology can create empty affinities, unsupported shared IRQ/private resource combinations, or unusable monitors without `arm,not-ready-us`.

## Test Signals

Direct KUnit coverage is included via `test_mpam_devices.c` when `CONFIG_MPAM_KUNIT_TEST` is enabled. It tests property sanitization, feature merging across RIS/vMSC/component/class shapes, and bitmap reset programming. Additional required signals are ACPI MSC discovery, CPU hotplug probing, IRQ registration/unregistration, PARTID/PMG requestor limit behavior, T241/CMN quirk paths, MPAM disable on error IRQ, monitor read/NRDY behavior, and resctrl setup/teardown integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_internal.h -->
# sources/distributed-fs/ceph-client/drivers/resctrl/mpam_internal.h

## Purpose

This header defines the shared internal contract for the Arm MPAM driver and its resctrl bridge. It contains core topology types, feature and quirk enumerations, monitor/config state, exported globals and helper prototypes, MMIO register offsets, bit definitions, and small allocation helpers for monitor IDs.

## Important APIs, Types, And Functions

Core topology types are `struct mpam_msc`, `struct mpam_msc_ris`, `struct mpam_vmsc`, `struct mpam_component`, and `struct mpam_class`. `struct mpam_config` stores per-PARTID control values and feature-valid bits. `struct mon_cfg` and `struct msmon_mbwu_state` model monitoring filters and preserved MBWU counter state. `struct mpam_resctrl_dom`, `struct mpam_resctrl_res`, and `struct mpam_resctrl_mon` are the private bridge objects used by `mpam_resctrl.c`.

`enum mpam_device_features` enumerates cache portion/capacity/associativity, memory bandwidth, priority, monitor, and PARTID narrowing capabilities. `enum mpam_device_quirks` captures T241 and CMN workarounds. `mpam_has_feature()`, `mpam_set_feature()`, and `mpam_clear_feature()` manipulate packed-safe feature bitmaps. `mpam_is_enabled()` reads the `mpam_enabled` static key.

The header declares `mpam_srcu`, `mpam_classes`, `mpam_partid_max`, `mpam_pmg_max`, device-layer APIs, monitor APIs, resctrl APIs, and fallback no-op resctrl stubs when `CONFIG_RESCTRL_FS` is off.

## Control Flow

There is no standalone runtime flow, but the header defines the state transitions used by the implementation: MSC discovery builds the topology structs, feature probing fills `mpam_props`, enable allocates per-component config arrays and monitor state, resctrl maps classes and components into domains, and disable/free paths use `mpam_garbage` for SRCU-safe teardown.

## State And Persistence

Most persistent MPAM driver state is shaped here. `struct mpam_msc` stores hardware identity, interface type, accessibility mask, probe status, register mapping, interrupts, locks, RIS list, error flags, and quirk state. `struct mpam_component` stores per-PARTID config arrays read by CPU hotplug callbacks. `struct mpam_msc_ris` stores RIS ID, feature props, reset state, affinity, and MBWU state.

State protected by SRCU may not be freed immediately, so `struct mpam_garbage` allows deferred `kfree()` or `devm_kfree()` after `synchronize_srcu()`. Monitor selector locking is currently valid only for MMIO MSCs and intentionally returns false for firmware-backed interfaces.

## Dependencies And Integration Points

The header integrates Linux resctrl, Arm MPAM architecture helpers, SRCU, bitmap APIs, cpumasks, IO accessors, jump labels, and generated ACPI MPAM types. Register definitions follow the Arm MPAM System Component specification and are consumed directly by `mpam_devices.c`.

## Risks And Edge Cases

The source snapshot contains duplicate enum and macro definitions, including duplicate `COUNT_BOTH` and duplicate `MPAMF_CPOR_IDR_CPBM_WD`, which are compile-integrity risks. `mpam_mon_sel_lock()` currently warns and fails for non-MMIO interfaces, so PCC support declared in device state is not practically implemented. Several structs rely on lock comments for correctness rather than type-level enforcement. `PACKED_FOR_KUNIT` changes `struct mpam_props` layout under tests to catch sanitization gaps, so tests intentionally alter packing assumptions.

## Test Signals

Compile coverage is the first signal because this header defines many shared symbols and macros. Runtime signals come from MPAM device probing, resctrl bridge compilation, and KUnit tests that exercise packed `mpam_props`, feature bit operations, and register constants used by bitmap reset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_resctrl.c -->
# sources/distributed-fs/ceph-client/drivers/resctrl/mpam_resctrl.c

## Purpose

This file maps Arm MPAM classes and components into the generic Linux resctrl filesystem architecture. It chooses MPAM resources that can represent L2/L3 cache allocation, memory bandwidth allocation, and L3 occupancy monitoring; initializes `struct rdt_resource` capabilities; translates resctrl CLOSID/RMID operations into MPAM PARTID/PMG values; manages resctrl domains during CPU hotplug; and tears resctrl down if MPAM is disabled.

## Important APIs, Types, And Functions

It implements the resctrl architecture hooks such as `resctrl_arch_alloc_capable()`, `resctrl_arch_mon_capable()`, `resctrl_arch_get_num_closid()`, `resctrl_arch_system_num_rmid_idx()`, `resctrl_arch_rmid_idx_encode()`, `resctrl_arch_rmid_idx_decode()`, `resctrl_arch_sched_in()`, `resctrl_arch_set_cpu_default_closid_rmid()`, `resctrl_arch_set_closid_rmid()`, `resctrl_arch_get_config()`, `resctrl_arch_update_one()`, `resctrl_arch_update_domains()`, `resctrl_arch_reset_all_ctrls()`, monitor context allocation/free, and `resctrl_arch_rmid_read()`.

MPAM-owned setup and hotplug functions are `mpam_resctrl_setup()`, `mpam_resctrl_exit()`, `mpam_resctrl_online_cpu()`, `mpam_resctrl_offline_cpu()`, and `mpam_resctrl_teardown_class()`. Resource selection helpers include `mpam_resctrl_pick_caches()`, `mpam_resctrl_pick_mba()`, `mpam_resctrl_pick_counters()`, `topology_matches_l3()`, and `traffic_matches_l3()`.

## Control Flow

`mpam_resctrl_setup()` waits for cacheinfo, initializes resctrl domain lists for all resource slots, selects MPAM classes for cache controls and MBA, initializes selected `rdt_resource` objects, selects monitoring counter classes, initializes monitoring, and then calls `resctrl_init()`. If neither allocation nor monitoring is available, setup returns `-EOPNOTSUPP`.

Resource selection is conservative. Cache allocation exposes only MPAM cache classes at level 2 or 3 with usable CPOR bitmaps, no more than 32 CBM bits, and affinity covering all possible CPUs. MBA uses MBW_MAX-capable classes whose topology and traffic shape match L3 expectations. Monitoring currently exposes CSU occupancy counters as L3 occupancy events and may fake an L3 resource when counters exist without L3 controls.

During CPU online, the bridge creates or updates control and monitor domains for each selected resource, using MPAM component affinity to choose domain membership and IDs. During CPU offline, it removes CPU bits, calls resctrl offline hooks, synchronizes RCU when a domain list entry is removed, and frees empty `mpam_resctrl_dom` objects.

Configuration updates convert resctrl CBM or MBA percentage values into `struct mpam_config` and call `mpam_apply_config()` for the correct PARTID. CDP emulation maps code/data to odd/even PARTIDs through `resctrl_get_config_index()`.

## State And Persistence

Static arrays `mpam_resctrl_controls[RDT_NUM_RESOURCES]` and `mpam_resctrl_counters[MPAM_MAX_EVENT + 1]` persist the chosen MPAM classes. `cdp_enabled`, per-resource `cdp_enabled`, `cacheinfo_ready`, and `resctrl_enabled` track bridge state. Domain lists live inside the `rdt_resource` objects and contain allocated `mpam_resctrl_dom` wrappers. Monitor context allocation uses IDA-backed CSU monitor allocation in the selected MPAM class; MBWU contexts currently use the sentinel `USE_PRE_ALLOCATED`.

Task and CPU default state is persistent in Arm MPAM task fields and `arm64_mpam_global_default`. CDP enable/disable relabels all tasks and updates all possible CPU defaults before syncing current CPU MPAM registers.

## Dependencies And Integration Points

The file depends on generic resctrl, cacheinfo, CPU hotplug, Arm MPAM task/register helpers, MPAM topology from `mpam_devices.c`, and `mpam_internal.h`. It assumes the generic resctrl model is L3-centered and adapts MPAM classes into that shape. It also depends on cacheinfo becoming ready at `device_initcall_sync()`.

## Risks And Edge Cases

Several resctrl hooks are stubs or unsupported: event configuration, RMID resets, counter assignment, IO allocation, and ABMC-style counter reading return no-op or errors. `resctrl_arch_rmid_read()` only accepts L3 occupancy events in this snapshot. The source contains a duplicated `tsk_closid >>= 1;` line in `resctrl_arch_match_rmid()`, which would incorrectly match tasks when CDP is enabled. CDP is warned as expert-only and rejected unless `CONFIG_EXPERT` allows it because repeated mounts can exhaust/out-range PARTIDs.

Topology inference is strict and may hide valid MPAM resources if cacheinfo, PPTT, NUMA, memory-side cache, or last-level-cache assumptions do not match resctrl's L3 model. Domain management must coordinate `domain_list_lock`, CPU hotplug locks, SRCU, and RCU list removal. Monitor allocation can sleep waiting for CSU monitor IDs.

## Test Signals

There is a conditional include for `test_mpam_resctrl.c`, though that file is outside this work item. Useful tests include class selection for L2/L3/MBA/CSU, MBA percent-to-fixed-point conversion, CDP enable/disable relabeling, CPU hotplug domain creation/removal, monitor context exhaustion and wakeup, occupancy reads through `mpam_msmon_read()`, and teardown when MPAM disable removes a class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/mpam_resctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_devices.c -->
# sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_devices.c

## Purpose

This file provides KUnit tests for internal MPAM device-layer helpers. It is intended to be included directly into `mpam_devices.c` under `CONFIG_MPAM_KUNIT_TEST`, giving tests access to static functions and static globals that are not exported.

## Important APIs, Types, And Functions

The test cases are `test__props_mismatch()`, `test_mpam_enable_merge_features()`, and `test_mpam_reset_msc_bitmap()`. A fake hierarchy of `mpam_class`, two `mpam_component` objects, two `mpam_vmsc` objects, two `mpam_msc` objects, and two `mpam_msc_ris` objects is reset by `reset_fake_hierarchy()`.

`test__props_mismatch()` validates that property merge/sanitization clears every field by comparing a zeroed parent to a child initialized with `0xff`. `test_mpam_enable_merge_features()` exercises how features merge across RIS in one vMSC, across different MSCs, and across different components. `test_mpam_reset_msc_bitmap()` allocates a fake MMIO buffer and verifies bitmap reset writes for widths 0, 1, 16, 32, and 33.

## Control Flow

The KUnit suite initializes fake list heads and fields, locks `mpam_list_lock` while invoking merge code, manipulates feature bits and property widths, calls `mpam_enable_merge_features()`, and asserts resulting class/vMSC properties. The bitmap test initializes a fake MSC, satisfies lockdep with `part_sel_lock`, and calls a wrapper that uses `guard(preempt)()` to avoid debug preemption warnings.

## State And Persistence

All fake objects are static globals reused across test cases after reset. The tests intentionally mutate global-style MPAM hierarchy state but do not persist anything outside the KUnit run. The fake MMIO buffer is KUnit-allocated and cleaned up by the framework.

## Dependencies And Integration Points

The tests depend on KUnit, static inclusion into `mpam_devices.c`, MPAM internal types and macros, and the Kconfig option `MPAM_KUNIT_TEST`. `PACKED_FOR_KUNIT` in `mpam_internal.h` supports these tests by making padding-sensitive property sanitization detectable.

## Risks And Edge Cases

Because the file is included into the implementation rather than compiled separately, symbol visibility and static globals are tightly coupled to `mpam_devices.c`. The fake hierarchy covers feature-merge shapes but does not exercise real ACPI parsing, CPU affinity, MMIO read/write ordering beyond bitmap writes, IRQ paths, or CPU hotplug. The tests assume static fake objects are always reset before use.

## Test Signals

The suite itself is the direct test signal for `__props_mismatch()`, `mpam_enable_merge_features()`, and `mpam_reset_msc_bitmap()`. Passing tests indicate feature mismatches are sanitized, alias versus non-alias merge behavior is preserved, and bitmap reset writes correct full and partial words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/resctrl/test_mpam_devices.c -->
