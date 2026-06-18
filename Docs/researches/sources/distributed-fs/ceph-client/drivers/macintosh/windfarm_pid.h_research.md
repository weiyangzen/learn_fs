# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.h

## Purpose
Declares Windfarm PID parameter and state structures used by PowerMac thermal model drivers and the PID implementation module.

## Important APIs, Types, And Functions
`struct wf_pid_param` captures simple PID interval, history length, additive mode, derivative/proportional/reset gains, input target, and output min/max. `struct wf_pid_state` stores first-run state, current sample index, current target, sample/error history, and a private copy of parameters. `struct wf_cpu_pid_param` adds CPU-specific `pmaxadj`, `ttarget`, and `tmax`; `struct wf_cpu_pid_state` stores power, error, and two-temperature histories plus `last_delta`. The header declares the four exported init/run functions.

## Control Flow
Callers fill a parameter struct from hardcoded Darwin-derived tables, SMU SDB partitions, or MPU EEPROM fields, then call the init function. Tick handlers call run functions and propagate the resulting target to Windfarm controls.

## State, Dependencies, And Integration
The header depends on kernel integer types through its includers and defines `WF_PID_MAX_HISTORY` and `WF_CPU_PID_MAX_HISTORY` as 32. It is included by all Windfarm model-controller files and by `windfarm_pid.c`.

## Risks And Test Signals
The maximum history constants are compile-time array sizes, but the run functions do not enforce them internally. Firmware-derived history lengths must be clamped by callers. Test signals are compile coverage of each model driver, history length validation, and thermal-loop startup with copied parameter values that remain stable even if the caller's stack struct goes away.
