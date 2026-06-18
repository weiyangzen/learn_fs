# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_powerclamp.c

## Purpose

`intel_powerclamp.c` registers a thermal cooling device that reduces package power by injecting forced idle time across selected CPUs, using idle injection and package C-state feedback.

## Important APIs, Types, and Functions

State is held in `struct powerclamp_data`, calibration array `cal_data[]`, cpumask, duration/window/max-idle parameters, and idle-inject device `ii_dev`. Cooling callbacks expose max/current/set state. `powerclamp_idle_injection_register()`, `trigger_idle_injection()`, `idle_inject_update()`, and `powerclamp_adjust_controls()` manage runtime idle injection and compensation. Debugfs exposes calibration data.

## Control Flow

Init checks Intel MWAIT and package C-state counters, allocates default CPU mask, registers cooling device, sets duration, and creates debugfs. Setting cooling state from zero starts idle injection; changing nonzero state adjusts runtime; setting zero stops and unregisters idle injection. The update callback periodically computes package C-state ratio, recalibrates compensation, and may skip an idle cycle when the package already meets target.

## State and Persistence Behavior

All state is in-memory module state. Module parameters persist only as runtime settings. Hardware feedback comes from package C-state MSRs; cooling action is scheduled idle injection.

## Dependencies and Integration Points

It depends on x86 MWAIT, package residency MSRs, `idle_inject`, thermal cooling devices, CPU masks, debugfs, and module parameters. Thermal governors can bind this cooling device to thermal zones.

## Risks and Test Signals

Risks include CPU mask/max-idle constraints, mutex trylock behavior in idle callback, delayed work after stop, calibration instability under external interrupts, and strong package topology assumptions. Test signals include module load gating, cpumask/max_idle/duration/window parameter validation, cooling state transitions, package C-state ratio reporting, debugfs creation, and unload while clamping.
