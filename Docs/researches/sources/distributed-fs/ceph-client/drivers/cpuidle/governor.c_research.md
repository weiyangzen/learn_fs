<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c

## Purpose

`governor.c` manages cpuidle governor registration, selection, and latency constraint lookup. Governors decide which idle state the core should enter on each idle loop iteration.

## Important APIs, Types, And Functions

It owns `param_governor`, `cpuidle_governors`, `cpuidle_curr_governor`, and `cpuidle_prev_governor`. `cpuidle_register_governor()` adds a governor and may switch to it based on boot parameter and rating. `cpuidle_find_governor()` performs case-insensitive lookup. `cpuidle_switch_governor()` disables all detected devices under the old governor, switches the pointer, re-enables devices, and reinstalls the idle handler. `cpuidle_governor_latency_req()` combines per-CPU device PM QoS, global CPU latency, and wakeup-latency QoS.

## Control Flow

Governors register during postcore init. Registration under `cpuidle_lock` rejects duplicate names, appends to the list, and switches if no governor exists, if the boot parameter names it, or if it has a higher rating than the current non-forced governor. Switching pauses idle entry by uninstalling the handler before reconfiguring devices.

## State And Persistence Behavior

The governor list and current/previous governor pointers persist for the kernel lifetime. Device governor state is reset through each governor's enable/disable hooks during switches.

## Dependencies And Integration Points

It integrates with cpuidle device lists, sysfs governor writes, PM QoS, CPU devices, and boot/module parameters.

## Risks And Test Signals

Risks include switching with devices enabled, rating/boot-parameter precedence mistakes, and latency constraint unit errors. Test by listing and changing governors in sysfs, booting with `cpuidle.governor`, setting PM QoS latency constraints, and validating device enable hooks run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c -->
