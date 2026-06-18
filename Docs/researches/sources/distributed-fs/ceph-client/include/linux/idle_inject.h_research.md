# sources/distributed-fs/ceph-client/include/linux/idle_inject.h

## Purpose
Declares the idle injection framework used by thermal/power code to force selected CPUs into idle for controlled durations.

## Important APIs, Types, And Functions
The opaque `idle_inject_device` is registered with `idle_inject_register()` or `idle_inject_register_full()`, the latter accepting an update callback. Control APIs are `idle_inject_unregister()`, `idle_inject_start()`, `idle_inject_stop()`, `idle_inject_set_duration()`, `idle_inject_get_duration()`, and `idle_inject_set_latency()`.

## Control Flow
A governor or cooling driver registers a cpumask, sets run/idle durations and optional latency, starts injection, and later stops/unregisters it. The implementation schedules periodic CPU idle forcing outside this header; the optional update callback lets the owner revise policy during operation.

## State And Persistence
State is runtime-only in the opaque device: target CPUs, active/inactive status, run and idle durations, latency constraints, timers/work, and optional callback. There is no persistent policy storage here.

## Dependencies And Integration Points
Uses `struct cpumask` and integrates with CPU idle, scheduler, thermal cooling, power management, and CPU hotplug behavior.

## Risks
Incorrect durations or latency can damage performance or thermal response. CPU hotplug and cpumask lifetime must be handled carefully. Callers need to stop injection before unregister and avoid sleeping/expensive work in update paths if implementation context is constrained.

## Test Signals
Thermal throttling tests, start/stop idempotence, duration get/set validation, latency behavior, CPU hotplug under active injection, cpumask edge cases, and tracing that confirms requested idle/run duty cycles.
