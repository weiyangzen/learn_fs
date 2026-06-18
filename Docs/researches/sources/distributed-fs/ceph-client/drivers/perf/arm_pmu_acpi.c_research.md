# sources/distributed-fs/ceph-client/drivers/perf/arm_pmu_acpi.c

## Purpose
ACPI discovery glue for ARM CPU PMUs and related per-CPU tracing devices. It parses MADT GICC PMU interrupt fields, requests per-CPU PMU IRQs before PMU registration, associates CPUs with homogeneous PMU instances by MIDR, and opportunistically creates ACPI platform devices for SPE and TRBE when their MADT interrupt fields are present.

## Important APIs, Types, And Functions
- `arm_pmu_acpi_probe()` is the exported entry used by the PMUv3 driver on ACPI systems.
- `arm_pmu_acpi_parse_irqs()` walks possible CPUs, converts GICC performance interrupt GSIs to Linux IRQs, and calls `armpmu_request_irq()`.
- `arm_pmu_acpi_associate_pmu_cpu()` records `probed_pmus` and fills per-CPU IRQ fields in the PMU's `hw_events`.
- `arm_pmu_acpi_cpu_starting()` is a CPUHP callback that associates late-starting CPUs before common PMU hotplug code runs.
- `arm_acpi_register_pmu_device()` registers homogeneous SPE/TRBE platform devices using ACPI GSI fields.

## Control Flow
`arm_pmu_acpi_probe()` first parses all PMU IRQs, then registers an ACPI-specific CPUHP startup state. It scans online CPUs, skips CPUs already associated with a PMU, allocates an `arm_pmu`, records the current CPU MIDR in `pmu->acpi_cpuid`, associates all online CPUs with the same MIDR, calls the architecture init function, gives each PMU a unique suffix, and registers it with `armpmu_register()`. SPE/TRBE registration happens earlier from `subsys_initcall(arm_pmu_acpi_init)`.

## State And Persistence
Per-CPU static variables `probed_pmus` and `pmu_irqs` store ACPI PMU ownership and IRQ numbers. State is runtime-only and rebuilt on boot. PMU names are dynamically allocated with `kasprintf()` for multiple heterogeneous PMUs.

## Dependencies And Integration Points
The file integrates ACPI MADT/GICC parsing, ACPI GSI registration, CPU topology heterogeneity IDs, common `arm_pmu.c` IRQ helpers, PMUv3 initialization, and platform-device registration for `ARMV8_SPE_PDEV_NAME` and `ARMV8_TRBE_PDEV_NAME`.

## Risks
The code assumes homogeneous interrupt layouts for SPE/TRBE and currently requires at least one CPU of a PMU class to be online during probe. GSI zero is rejected pragmatically despite being spec-valid. Error paths after allocation can leak some previously allocated PMUs or names because this probe path mostly returns immediately on failures. PPI mismatch detection prevents unsafe mixed IRQ layouts, but bad firmware can still leave CPUs unassociated.

## Test Signals
ACPI boot with PMUv3 should show PMU registration and no `Unable to associate CPU` warnings. Validate `/sys/bus/event_source/devices/armv8_pmuv3_*`, perf on heterogeneous ACPI systems, CPU hotplug association, invalid or zero GSI handling, and ACPI SPE/TRBE platform device creation when MADT fields are present.
