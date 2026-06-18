# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-core.c

## Purpose

This file implements the ETMv4/ETE CoreSight source driver. It supports AMBA memory-mapped ETMv4 devices and platform-described sysreg/ETE devices, discovers hardware capabilities, registers CPU-affine CoreSight sources, programs trace units for sysfs and perf sessions, handles perf filters and AUX pause/resume, integrates CoreSight syscfg, manages CPU hotplug and CPU power-management save/restore, and provides trace filtering for kernel/user/host/guest exception levels.

## Important APIs, Types, and Functions

Key flows include sysreg/ETE accessors, OS/software lock helpers, FEAT_TRF trace filtering, `etm4_enable_hw()`, `etm4_disable_hw()`, `etm4_parse_event_config()`, `etm4_config_timestamp_event()`, `etm4_set_event_filters()`, perf pause/resume, `etm4_init_arch_data()`, CPU PM save/restore, AMBA/platform/delayed probing, and `etm4_add_coresight_dev()`.

## Control Flow

Initialization registers CPU PM/hotplug callbacks, then AMBA and platform drivers. Probe allocates driver data, maps MMIO if present, enables clocks/runtime PM, determines CPU affinity, and runs architecture discovery on the target CPU. If the CPU is offline, probe stores delayed init state and completes registration from the online callback. Successful discovery selects MMIO when available, otherwise sysreg/ETE access if CPU debug feature registers support it.

Perf enable verifies CPU affinity, takes CoreSight perf mode, parses perf config, stores the path trace ID, records initial AUX pause state, and programs hardware. Sysfs enable optionally enables an active configfs/syscfg preset, stores the trace ID, marks the session unpaused, and runs enable on the owning CPU. Hardware enable disables the trace unit, waits for idle, writes every supported config register family based on discovered counts, sets trace ID and power-up, and enables the trace unit unless the perf session starts paused.

Disable reverses this flow, saves counter/single-shot status, releases configfs active config where needed, and returns CoreSight mode to disabled. CPU PM save/restore snapshots trace registers on power-down and restores them on exit when self-hosted context save is required.

## State and Persistence

`struct etmv4_drvdata` stores discovered capability fields, access type, OS lock model, trace filtering value, clocks, CPU, CoreSight device, trace ID, paused flag, save-state pointer, boot/sticky enable flags, and the mutable `struct etmv4_config`. Disable updates cached single-shot status and counter values. Delayed probe state persists per CPU until completion or removal.

## Dependencies and Integration Points

The driver integrates CoreSight source APIs, CoreSight trace-ID allocation, the perf ETM PMU layer, CoreSight syscfg, AMBA and platform buses, OF/ACPI matching, runtime PM, CPU hotplug, CPU PM notifiers, KVM tracing filter configuration, architecture sysreg accessors, and ETM4 sysfs groups.

## Risks and Test Signals

System-register trace access requires strict barriers. Perf timestamp event generation consumes a free counter and resource selector. Branch broadcast perf requests fail if unsupported because silent decode errors are possible. CPU PM save/restore is large and register-count dependent. `__etm4_cpu_save()` and restore appear to use `trcvmidcctlr0` for the second VMID mask path where `trcvmidcctlr1` would be expected. Test AMBA/sysreg/ETE probe, delayed probe, sysfs/perf enable, AUX pause/resume, filters, syscfg presets, timestamp resources, branch broadcast rejection, CPU hotplug, CPU PM save/restore, FEAT_TRF filtering, and trace ID stability.
