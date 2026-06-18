# sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/cpu-on-off-test.sh

## Purpose

`cpu-on-off-test.sh` validates CPU hotplug sysfs control by offlining and onlining one CPU by default or all hotpluggable CPUs with `-a`.

## Important APIs, Types, and Functions

It uses `taskset`, `mount -t sysfs`, `/sys/devices/system/cpu/{online,offline,present}`, per-CPU `cpuN/online`, and helpers `hotpluggable_cpus()`, `cpu_is_online()`, `online_cpu()`, `offline_cpu()`, expectation wrappers, and all-CPU online/offline loops.

## Control Flow

`prerequisite()` requires root, pins the script to CPU0, locates sysfs, confirms CPU hotplug support, and records online/offline/present ranges. Default mode offlines and re-onlines `online_max`, then, if an offline CPU exists, onlines/offlines `present_max` and restores it online. Full mode onlines all offline CPUs, offlines all online hotpluggable CPUs except a reserve CPU, then onlines all again.

## State and Persistence Behavior

The script mutates CPU hotplug state by writing 0/1 to per-CPU `online` files. Default mode attempts to leave CPUs in their original state; full mode ends with all hotpluggable CPUs online. `retval` accumulates failures.

## Dependencies and Integration Points

It requires root, sysfs, more than one CPU, CPU hotplug support, and a shell with Bash features. It integrates with kernel CPU hotplug paths and kselftest skip code 4.

## Risks and Edge Cases

Offlining CPUs is intrusive and can disrupt workloads or tests pinned to affected CPUs. The parsing of CPU range strings uses simple suffix extraction and assumes common range forms. The `present_max` restoration path uses `online_cpu` without expectation checking at the end.

## Test Signals

Pass signals are successful writes and matching sysfs state checks after every online/offline operation. Failures report unexpected success/failure or wrong online/offline state.
