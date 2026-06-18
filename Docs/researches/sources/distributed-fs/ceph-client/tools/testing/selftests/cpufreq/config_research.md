# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/config

## Purpose

This config declares kernel cpufreq features and governors needed by the cpufreq selftests.

## Important APIs, Types, and Functions

It requests `CONFIG_CPU_FREQ`, `CONFIG_CPU_FREQ_STAT`, and governors `POWERSAVE`, `USERSPACE`, `ONDEMAND`, `CONSERVATIVE`, and `SCHEDUTIL`.

## Control Flow

There is no executable flow; config tooling uses these symbols to determine expected kernel capability.

## State and Persistence Behavior

It persists only feature requirements.

## Dependencies and Integration Points

The shell tests expect `/sys/devices/system/cpu/cpufreq` policy directories, governor switching, stats, and optional module testing to align with these symbols.

## Risks and Edge Cases

The config does not guarantee hardware has a cpufreq driver or that every governor is available as a module/built-in. Tests still skip/fail based on runtime sysfs state.

## Test Signals

Kernels with these options should expose enough cpufreq functionality for basic and governor tests.
