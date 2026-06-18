# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpu.sh

## Purpose

`cpu.sh` provides CPU enumeration and hotplug helper functions for the cpufreq tests.

## Important APIs, Types, and Functions

It defines include guards, sources `cpufreq.sh`, and implements `for_each_cpu()`, `for_each_non_boot_cpu()`, `offline_cpu()`, `online_cpu()`, `reboot_cpu()`, `reboot_cpus()`, `print_unmanaged_cpus()`, and `count_cpufreq_managed_cpus()`.

## Control Flow

Callers set `CPUROOT` and then use iteration helpers to invoke commands over `cpuN` directories. `reboot_cpus()` repeatedly offlines and onlines all non-boot CPUs. Counting and warning helpers inspect per-CPU `cpufreq` directories.

## State and Persistence Behavior

The script mutates CPU online state through `$CPUROOT/$cpu/online`. It reads cpufreq directory presence and maintains only shell-local include guard state.

## Dependencies and Integration Points

It is sourced by `main.sh`, `cpufreq.sh`, `governor.sh`, `module.sh`, and `special-tests.sh`. It depends on root permissions for hotplug writes and sysfs layout.

## Risks and Edge Cases

CPU enumeration uses `ls | grep "cpu[0-9].*"` and boot CPU filtering uses `cpu[1-9].*`, which can include multi-digit CPUs but assumes CPU0 is the only boot CPU to avoid. Hotplug failures propagate through shell command errors only if callers check them.

## Test Signals

Expected signals are printed online/offline actions, managed CPU counts, and warnings for CPUs without cpufreq directories.
