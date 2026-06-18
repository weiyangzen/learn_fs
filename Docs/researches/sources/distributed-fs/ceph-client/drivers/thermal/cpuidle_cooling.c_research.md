# sources/distributed-fs/ceph-client/drivers/thermal/cpuidle_cooling.c

## Purpose
Generic thermal cooling-device implementation using cpuidle idle injection. It registers cooling devices from CPU DT `thermal-idle` child nodes and maps thermal state 0..100 to an injected idle ratio.

## Important APIs, Types, and Functions
- `struct cpuidle_cooling_device` stores the idle-inject device and current thermal state.
- `cpuidle_cooling_runtime()` computes run duration from fixed idle duration and requested idle percentage.
- Thermal callbacks `cpuidle_cooling_get_max_state()`, `cpuidle_cooling_get_cur_state()`, and `cpuidle_cooling_set_cur_state()` expose state and update idle injection.
- `__cpuidle_cooling_register()` creates the idle injection device, reads optional `duration-us` and `exit-latency-us`, registers the thermal cooling device, and names it from the first CPU device.
- `cpuidle_cooling_register()` scans each CPU in a cpuidle driver's mask for a `thermal-idle` child node.

## Control Flow
For each CPU in the cpuidle driver's mask, the public registration helper obtains the CPU OF node and its `thermal-idle` child. If present, it registers an idle-injection-backed cooling device for the driver's cpumask. Setting state records the new percentage, reads the idle duration, calculates runtime, updates idle-injection timing, starts injection when transitioning from 0 to nonzero, and stops it when transitioning back to 0.

## State and Persistence
The current cooling state and idle-inject handle are in memory. The injected idle timing lives in the idle-inject subsystem until changed or unregistered after registration failure. There is no explicit unregister API in this file.

## Dependencies and Integration Points
Depends on cpuidle drivers, idle injection, thermal cooling devices, OF CPU nodes, and optional `duration-us`/`exit-latency-us` properties.

## Risks and Edge Cases
- `state` is treated as a percent but `set_cur_state()` does not clamp to max; it relies on thermal core callers.
- `cpuidle_cooling_register()` can encounter multiple CPUs with the same driver cpumask and register more than intended if multiple CPUs expose `thermal-idle` nodes.
- `get_cpu_device(cpumask_first())` is assumed valid before `dev_name()`.
- Registration has no public cleanup path for successful devices in this file.

## Test Signals
Tests should cover runtime formula for 0, 50, and 100 percent, DT property defaults and overrides, idle injection start/stop transitions, failure cleanup paths, and multi-CPU cpumask registration behavior.
