<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c

## Purpose

`cpuidle-tegra.c` implements ARM cpuidle states for Tegra20, Tegra30, Tegra114, and Tegra124. It exposes C1 WFI, C7 CPU-core power gating, and CC6 CPU-cluster power gating where the SoC and power-management firmware support them.

## Important APIs, Types, And Functions

`tegra_idle_driver` defines the cpuidle states. `tegra_cpuidle_enter()` is the common enter callback and adjusts Tegra30 CPU0 C7 requests into C1 or CC6 when necessary. Deep states use `tegra_cpuidle_state_enter()`, which disables FIQs, marks LP2 entry, calls CPU PM and context tracking, and dispatches to `tegra_cpuidle_c7_enter()` or `tegra_cpuidle_cc6_enter()`. CC6 coordination uses `tegra_cpuidle_coupled_barrier()`, `tegra_idle_barrier`, and `tegra_abort_flag`.

## Control Flow

Probe waits for PMC suspend mode, disables states according to DT/PM_SLEEP/SoC limitations, applies Tegra114-style C7 latency and s2idle setup where applicable, and registers the driver with coupled CPUs. CC6 requires secondary CPUs to park, CPU0 to wait for rail-off readiness, entry to LP2, and then unpark of secondaries on exit. C7 may call trusted firmware `prepare_idle` before `cpu_suspend()`.

## State And Persistence Behavior

State selection is mostly static after probe, but `tegra_cpuidle_pcie_irqs_in_use()` can disable CC6 on Tegra20 if PCIe IRQ loss risk is detected. Coupled barrier and abort flag are transient global synchronization state. Hardware flow controller, PMC, CPU clocks, reset, and GIC coupling hold persistent power state.

## Dependencies And Integration Points

It integrates with Tegra PMC, PM, flow controller, fuse/chip ID, trusted foundations firmware, ARM `cpu_suspend`, CPU PM, local FIQ control, coupled cpuidle, and PCIe workaround users through an exported symbol.

## Risks And Test Signals

Risks include secondary CPU parking timeouts, lost SGIs during GIC shutdown, incorrect state disabling by SoC ID or suspend mode, and CC6/PCIe interrupt loss. Test by booting all supported Tegra SoCs, inspecting state availability, exercising CPU hotplug-like parking paths, running suspend/resume and s2idle, using PCIe on Tegra20, and tracing failed deep-state entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c -->
