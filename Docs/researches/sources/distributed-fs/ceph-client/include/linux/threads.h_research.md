<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/threads.h -->
# sources/distributed-fs/ceph-client/include/linux/threads.h

## Purpose
defines global CPU/thread/PID sizing constants such as `NR_CPUS`, PID maximum defaults, root thread reserve, and per-CPU PID heuristics.

## Important APIs, Types, and Functions
The file is 47 lines and exports these visible symbol families: types/enums none; macros/constants `CONFIG_NR_CPUS`, `NR_CPUS`, `MIN_THREADS_LEFT_FOR_ROOT`, `PID_MAX_DEFAULT`, `PID_MAX_LIMIT`, `PIDS_PER_CPU_DEFAULT`, `PIDS_PER_CPU_MIN`; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Core PID and scheduler setup code uses these constants to size static CPU masks, choose default `/proc/sys/kernel/pid_max`, and derive thread limits.

## State and Persistence Behavior
No runtime state is stored here; constants influence compile-time sizing and boot-time tunables.

## Dependencies and Integration Points
It depends on configuration options such as CONFIG_NR_CPUS and CONFIG_BASE_SMALL plus PAGE_SIZE and long width from surrounding headers. Direct includes are none.

## Risks and Edge Cases
Using `NR_CPUS` for large static allocations wastes memory; code should prefer dynamic cpumasks when possible. PID limit values are ABI-visible through proc/sysctl behavior.

## Test Signals
Build small and large NR_CPUS configurations, validate pid_max defaults on 32-bit and 64-bit builds, and run fork/thread-limit stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/threads.h -->
