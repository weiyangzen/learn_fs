<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuidle.h

## Purpose

`cpuidle.h` defines the generic CPU idle power-management framework: idle state descriptors, per-CPU idle device state, driver registration, governor registration, state selection/entry, suspend-to-idle helpers, and CPU PM wrapped idle entry macros. The source was read as a complete 356-line file.

## Important APIs, Types, and Functions

Important types include `struct cpuidle_state_usage`, `struct cpuidle_state`, `struct cpuidle_device`, `struct cpuidle_driver`, and `struct cpuidle_governor`. APIs include `disable_cpuidle()`, `cpuidle_select()`, `cpuidle_enter()`, `cpuidle_reflect()`, `cpuidle_register_driver()`, `cpuidle_register_device()`, `cpuidle_register()`, pause/resume helpers, `cpuidle_enable_device()`, `cpuidle_disable_device()`, `cpuidle_play_dead()`, `cpuidle_get_cpu_driver()`, `cpuidle_get_device()`, `cpuidle_find_deepest_state()`, `cpuidle_enter_s2idle()`, `cpuidle_use_deepest_state()`, `sched_idle_set_state()`, `default_idle_call()`, and governor registration. Macros include `CPU_PM_CPU_IDLE_ENTER*()` variants.

## Control Flow

Drivers register ordered idle states and devices. Governors select a state based on latency/residency and tick-stop constraints. `cpuidle_enter()` invokes the selected state's `enter`, `enter_dead`, or `enter_s2idle` callback. The CPU PM idle macros handle index zero by calling `cpu_do_idle()`, otherwise optionally send CPU PM notifications, enter/exit context tracking, invoke the low-level idle function, and return either the state index or `-1`.

## State and Persistence Behavior

`struct cpuidle_device` persists per CPU and tracks registration/enabled flags, last state, residency, poll limits, usage counters, sysfs kobjects, and coupled idle state. `struct cpuidle_driver` persists registered state metadata, safe state, cpumask, and governor preference. State usage counters are in-memory statistics exposed by the framework.

## Dependencies and Integration Points

It depends on percpu storage, lists, hrtimers, and context tracking. It integrates with scheduler idle, CPU PM notifiers, RCU/context tracking, tick broadcast, sysfs, suspend-to-idle, architecture idle instructions, coupled idle states, and governors.

## Risks and Edge Cases

`enter_s2idle` must not re-enable interrupts or manipulate clock event state when timekeeping is suspended. State flags such as `TIMER_STOP`, `RCU_IDLE`, and `COUPLED` must match callback behavior. Disabled-config stubs return `-ENODEV`. Coupled idle requires careful multi-CPU barriers. Context-tracking enter/exit ordering is lockdep-sensitive.

## Test Signals

Signals include cpuidle driver registration, state selection and reflect tests, sysfs usage counters, suspend-to-idle on deep states, CPU hotplug play-dead, RCU idle warnings, tick-stop behavior, coupled idle tests, and builds with `CONFIG_CPU_IDLE=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle.h -->
