# sources/distributed-fs/ceph-client/drivers/edac/a72_edac.c Research

## Purpose
This driver reports ARM Cortex-A72 L1 CPU RAM and L2 cache ECC/parity syndrome state through the EDAC device framework. It polls compatible CPUs, reads architectural implementation-defined syndrome registers, clears valid reports, and reports correctable versus fatal events.

## Important APIs, Types, and Functions
Key register definitions are `SYS_CPUMERRSR_EL1` and `SYS_L2MERRSR_EL1`, with valid/fatal bits and fields for L1 RAM ID and L2 CPUID/WAY. `struct mem_err_synd_reg` carries per-CPU CPU/L2 syndrome snapshots. `report_errors()` decodes and reports EDAC CE/UE events. `read_errors()` runs on the target CPU via SMP call and clears valid syndrome registers. `a72_edac_check()` iterates online compatible CPUs under `cpus_read_lock()`. `a72_edac_probe()` allocates and registers `struct edac_device_ctl_info`; `a72_edac_driver_init()` discovers compatible CPU device-tree nodes with `edac-enabled`.

## Control Flow
Module init scans all possible CPUs for `compatible = "arm,cortex-a72"` and an `edac-enabled` property, records them in `compat_mask`, creates a simple platform device, then registers the platform driver. Probe allocates one EDAC device named `cpu` with one instance per possible CPU and two blocks per instance (`L` block 0 for L1 and block 1 for L2). EDAC polling calls `a72_edac_check()`, which synchronously invokes `read_errors()` on each online CPU in `compat_mask`; `report_errors()` then emits `edac_device_handle_ce()` or `edac_device_handle_ue()` based on the fatal bit.

## State and Persistence
Persistent driver state is small: the global `compat_mask`, global `a72_pdev`, and the EDAC device control object stored in platform drvdata. Hardware syndrome state exists in CPU system registers until read and cleared. The driver does not persist counters itself; EDAC core tracks reported events.

## Dependencies and Integration Points
The driver depends on ARM64 system register access, SMP cross-calls, Open Firmware CPU nodes, platform-device registration, and EDAC device APIs from `edac_module.h`. Device-tree integration requires CPU nodes to opt in with `edac-enabled`; without that property the driver silently does not register a device.

## Risks and Edge Cases
The driver only scans possible CPUs at module init, so CPU nodes or properties must be present then. It skips offline CPUs during checks, so errors on offline CPUs are not read until they come online and are polled. Syndrome registers are cleared immediately after a valid read; if reporting later failed, the hardware status would already be consumed. Fatal cache errors are reported as EDAC UEs but no panic policy is implemented here.

## Test Signals
Build with `CONFIG_EDAC_CORTEX_A72` on ARM64. Runtime smoke tests need Cortex-A72 CPU DT nodes with `edac-enabled` and should show an EDAC device for `a72-edac`. Hardware or firmware-assisted error injection can validate that L1 RAM IDs map to the expected messages and that L2 CPUID/WAY is included. Hotplug tests should verify `cpus_read_lock()` iteration remains stable.
