# sources/distributed-fs/ceph-client/drivers/cpufreq/apple-soc-cpufreq.c

## Purpose

This driver controls CPU cluster DVFS performance states on Apple SoCs. It uses device-tree performance domains to find a cluster MMIO register block, converts OPP levels to Apple p-state indexes, and implements cpufreq target and fast-switch operations.

## Important APIs, types, and functions

`struct apple_soc_cpufreq_info` describes SoC-specific p-state bit layouts and maximum p-state values for S5L8960X, T8103, T8112, and fallback compatibles. `struct apple_cpu_priv` stores the CPU device, mapped register base, and SoC info. Key functions are `apple_soc_cpufreq_find_cluster()`, `apple_soc_cpufreq_init()`, `apple_soc_cpufreq_get_rate()`, `apple_soc_cpufreq_set_target()`, and `apple_soc_cpufreq_fast_switch()`.

## Control flow, state, and persistence

Module init only registers the cpufreq driver on `"apple,arm-platform"`. Policy init loads OPPs from DT, resolves the performance-domain phandle, maps the cluster registers, marks sharing CPUs, builds a cpufreq table, and stores each OPP level in `driver_data` as the p-state. Target waits for `APPLE_DVFS_CMD_BUSY` to clear, writes PS1 and optionally PS2 fields plus the SET bit, and returns immediately. Current frequency reads the current p-state field from status when known, otherwise falls back to the command register. Hardware register state persists until firmware or reset changes it; driver state is per-policy allocated data and OPP table state.

## Dependencies and integration points

The driver depends on device-tree CPU OPP tables, `performance-domains`, MMIO mapping, OPP sharing, cpufreq generic table verification, cooling-device integration, software boost, energy-model registration through OPP, and generic suspend handling. It is blocklisted from generic `cpufreq-dt` platform-device creation so it can own Apple-specific DVFS registers.

## Risks and test signals

Risks include SoC-specific bitfield mistakes, fallback status reads not reflecting boost limits, mapping the wrong performance-domain node, OPP level values exceeding known p-state fields, and transition timeout failures. Test signals are successful policy creation per cluster, correct p-state readback for every OPP, fast-switch operation, suspend frequency selection, EM registration, thermal cooling registration, and stable frequency changes on supported Apple SoCs.
