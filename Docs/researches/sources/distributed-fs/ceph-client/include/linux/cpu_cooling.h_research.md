<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h

## Purpose

`cpu_cooling.h` declares the bridge between CPU frequency/idle frameworks and the thermal cooling-device framework. It lets cpufreq policies and cpuidle drivers appear as thermal actuators. The source was read as a complete 72-line file.

## Important APIs, Types, and Functions

For `CONFIG_CPU_FREQ_THERMAL`, it declares `cpufreq_cooling_register()`, `cpufreq_cooling_unregister()`, and `of_cpufreq_cooling_register()`. Without that config, registration returns `ERR_PTR(-ENOSYS)` or `NULL`, and unregister is a no-op. For `CONFIG_CPU_IDLE_THERMAL`, it declares `cpuidle_cooling_register()`, otherwise a no-op inline is supplied.

## Control Flow

CPU frequency drivers register a cooling device after a policy is available; thermal zones can then throttle maximum frequency through that cooling device. Device-tree-aware platforms use the OF registration helper to bind cooling maps. Cpuidle drivers can register idle-state based cooling when supported.

## State and Persistence Behavior

The header owns no state. Registered `struct thermal_cooling_device` objects and their links to cpufreq policies or cpuidle drivers are managed by implementation files and persist until explicitly unregistered or driver removal occurs.

## Dependencies and Integration Points

It depends on `linux/of.h`, `linux/thermal.h`, and forward declarations of `struct cpufreq_policy` and `struct cpuidle_driver`. It integrates cpufreq, cpuidle, thermal governors, and device tree cooling maps.

## Risks and Edge Cases

Callers must handle disabled-config stubs and not assume a non-NULL cooling device. Unregister must only receive valid devices from successful registration. Thermal throttling correctness depends on cpufreq policy sharing, OPP data, and cooling maps matching the actual CPU domain.

## Test Signals

Signals include build coverage with and without CPU thermal configs, DT thermal-zone cooling-map binding, cpufreq policy removal cleanup, thermal governor requests reducing CPU max frequency, and cpuidle cooling registration on supported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_cooling.h -->
