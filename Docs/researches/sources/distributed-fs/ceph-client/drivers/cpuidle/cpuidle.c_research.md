<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c

## Purpose

`cpuidle.c` is the cpuidle core: it owns per-CPU cpuidle devices, dispatches governor-selected idle states, records residency statistics, handles suspend-to-idle entry, and manages device registration, enablement, sysfs creation, and idle-handler installation.

## Important APIs, Types, And Functions

Global state includes per-CPU `cpuidle_devices` and `cpuidle_dev`, `cpuidle_lock`, `cpuidle_detected_devices`, `enabled_devices`, `off`, and `initialized`. Public APIs include `cpuidle_select()`, `cpuidle_enter()`, `cpuidle_enter_state()`, `cpuidle_reflect()`, `cpuidle_use_deepest_state()`, `cpuidle_register_device()`, `cpuidle_unregister_device()`, `cpuidle_register()`, `cpuidle_unregister()`, `cpuidle_pause()`, and `cpuidle_resume()`.

## Control Flow

Registration installs a driver, initializes each per-CPU device, creates CPU sysfs, enables governor state, and installs the idle handler when at least one device is enabled. Idle entry writes the next hrtimer, routes coupled states through coupled machinery, switches to broadcast timers when local timers stop, leaves the MM if requested, enters RCU idle/context tracking as needed, calls the driver's state callback, restores IRQ/tick state, and updates usage, time, rejected, above, and below counters.

## State And Persistence Behavior

Per-device `states_usage`, last residency, next hrtimer, polling limit, forced latency limit, and registration flags persist across idle entries. The module parameter `off` disables cpuidle at boot, while `param_governor` is declared here for governor selection. Sysfs user disables are recorded in state usage.

## Dependencies And Integration Points

It integrates with governors, tick/nohz and broadcast timers, hrtimers, scheduler idle state, RCU/context tracking, CPU hotplug-style registration, suspend-to-idle, PM QoS, sysfs, module ownership, tracepoints, and optional coupled idle support.

## Risks And Test Signals

Risks include IRQ state leaks from drivers, incorrect RCU-idle flags, stale scheduler idle-state pointers, racey governor switches, and bad accounting when enter callbacks reject states. Test by toggling governors and per-state sysfs disables, enabling s2idle, running timer-stop states, validating tracepoints, checking residency counters, and exercising driver register/unregister error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c -->
