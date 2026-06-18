# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.h

## Purpose

This header defines the small platform-data interface used by `cpufreq-dt` setup helpers and declares the helper for registering a `cpufreq-dt` platform device.

## Important APIs, types, and functions

`struct cpufreq_dt_platform_data` carries optional behavior: `have_governor_per_policy`, `get_intermediate`, `target_intermediate`, `suspend`, and `resume`. `cpufreq_dt_pdev_register()` is exported by `cpufreq-dt.c` for code that wants to instantiate the generic driver under a parent device.

## Control flow, state, and persistence

The header has no runtime flow. Its fields are consumed at `dt_cpufreq_probe()` time to mutate the generic cpufreq driver callbacks and flags before registering the driver. Because the callbacks live in a global `cpufreq_driver`, platform data effectively influences the singleton driver instance.

## Dependencies and integration points

The header depends only on Linux types and forward-declares `struct cpufreq_policy`. It is included by `cpufreq-dt.c`, `cpufreq-dt-platdev.c`, and platform setup drivers such as Armada 37xx.

## Risks and test signals

Risks include adding platform-data fields without updating the singleton driver mutation logic, and assuming multiple independent `cpufreq-dt` instances can carry different callbacks at the same time. Test signals are successful compilation of users, correct suspend/resume hook invocation for platform helpers, and no callback leakage across incompatible platforms.
