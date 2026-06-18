<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h

## Purpose

`cpuhotplug.h` defines the CPU hotplug state machine and registration APIs for startup and teardown callbacks. It is the ordering contract that kernel subsystems use to run per-CPU setup and cleanup as CPUs transition offline, starting, online, active, and dead. The source was read as a complete 526-line file.

## Important APIs, Types, and Functions

`enum cpuhp_state` defines ordered states across PREPARE, STARTING, and ONLINE sections, including dynamic ranges `CPUHP_BP_PREPARE_DYN` and `CPUHP_AP_ONLINE_DYN`. Registration APIs include `__cpuhp_setup_state()`, `__cpuhp_setup_state_cpuslocked()`, wrappers `cpuhp_setup_state()`, `cpuhp_setup_state_cpuslocked()`, nocalls variants, `cpuhp_setup_state_multi()`, instance add/remove helpers, `cpuhp_remove_state()`, `cpuhp_remove_state_nocalls()`, `cpuhp_remove_multi_state()`, and `cpuhp_online_idle()`. Architecture synchronization hooks include `cpuhp_ap_sync_alive()`, `arch_cpuhp_sync_state_poll()`, `arch_cpuhp_cleanup_kick_cpu()`, `arch_cpuhp_kick_ap_alive()`, `arch_cpuhp_init_parallel_bringup()`, `cpuhp_ap_report_dead()`, and `arch_cpuhp_cleanup_dead_cpu()`.

## Control Flow

CPU online invokes startup callbacks sequentially from `CPUHP_OFFLINE + 1` to `CPUHP_ONLINE`. CPU offline invokes teardown callbacks in reverse from `CPUHP_ONLINE - 1` down to offline. PREPARE callbacks run on a control CPU, STARTING callbacks run on the hotplugged CPU with interrupts disabled, and ONLINE callbacks run from the per-CPU hotplug thread with interrupts and preemption enabled. Multi-instance states add per-object callbacks after a state is prepared.

## State and Persistence Behavior

The hotplug core stores callback registrations and per-instance hlist nodes outside this header. Dynamic state allocations and registered instances persist until removed. The enum values are effectively a global ordering ABI inside the kernel.

## Dependencies and Integration Points

It depends on `linux/types.h` and forward-declared hlist/task types through included context. Integration points span scheduler, RCU, timers, IRQ controllers, perf, workqueues, block, networking, cpuidle, ACPI, architecture timers, watchdogs, random, KVM, and architecture bringup/dead-CPU synchronization.

## Risks and Edge Cases

Wrong state choice can run callbacks under the wrong CPU, interrupt, or preemption context. Startup failures must be unwound in reverse order. Multi-instance states require all instances to be removed before the state callback is removed. Dynamic states avoid unnecessary enum growth, but explicit ordering constraints must be modeled in the enum. Cpuslocked variants must only be used while the CPU read lock is held.

## Test Signals

Signals include CPU hotplug torture, callback ordering instrumentation, failure-injection in startup callbacks, multi-instance add/remove tests, dynamic state allocation exhaustion, !SMP builds, architecture parallel bringup tests, and lockdep validation for cpuslocked variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhotplug.h -->
