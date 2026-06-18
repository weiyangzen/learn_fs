# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c

## Purpose

This file decides whether to create the generic `cpufreq-dt` platform device from device tree. It preserves legacy allowlisted machines, supports automatic creation for CPU0 OPP v2 bindings, and blocks machines that need specialized cpufreq drivers.

## Important APIs, types, and functions

The main data is `allowlist[]` and `blocklist[]` of root compatible strings. `cpu0_node_has_opp_v2_prop()` checks whether CPU0 has `operating-points-v2`. `cpufreq_dt_platdev_init()` performs the policy decision and calls `platform_device_register_data()` with optional `struct cpufreq_dt_platform_data`.

## Control flow, state, and persistence

At core init, the file first checks the allowlist and carries match data into platform data when present, such as per-policy governor support for RK3399. If not allowlisted, it creates the device when CPU0 has OPP v2 and the root compatible is not blocklisted. Otherwise it returns `-ENODEV`. The only lasting state is the registered platform device; this file has no remove path because it is built as an init helper.

## Dependencies and integration points

It depends on OF machine matching, CPU device-tree nodes, platform-device registration, and the `cpufreq_dt_platform_data` contract from `cpufreq-dt.h`. It integrates with many SoC-specific cpufreq drivers by explicitly not creating `cpufreq-dt` for platforms that need custom handling, including Apple, MediaTek, NVIDIA Tegra, Qualcomm, TI, and others.

## Risks and test signals

Risks include allowlist/blocklist drift, incorrect automatic creation on platforms whose OPP v2 data still requires custom voltage/clock sequencing, and missing creation for legacy OPP v1 systems. Test signals are exactly one cpufreq driver binding per platform, successful `cpufreq-dt` creation on allowlisted or unblocked OPP v2 machines, and absence of conflicts on blocklisted platforms.
