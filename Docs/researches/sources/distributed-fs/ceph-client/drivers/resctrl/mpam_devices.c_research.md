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
