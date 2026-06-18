# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pid.c

## Purpose
Implements reusable fixed-point PID algorithms for Windfarm thermal control loops: a general single-input PID and a CPU-specific controller that combines power and temperature.

## Important APIs, Types, And Functions
Exports `wf_pid_init()`, `wf_pid_run()`, `wf_cpu_pid_init()`, and `wf_cpu_pid_run()`. The simple PID stores sample/error history, calculates integral and derivative terms over `history_len`, applies gains shifted by 36 bits, optionally adds to the previous target, and clamps to min/max. The CPU PID computes power error against `pmaxadj`, uses the integral term to adjust an effective temperature target, derives temperature change from a two-sample history, applies proportional temperature error, and updates/clamps the output target.

## Control Flow
Model drivers initialize state once when all required sensors and controls are present. Each Windfarm tick passes the latest fixed-point sensor values into the appropriate run function and applies the returned target to one or more fans or pumps.

## State, Dependencies, And Integration
All persistent state lives in caller-owned `wf_pid_state` or `wf_cpu_pid_state` objects. The module depends only on integer arithmetic and exported kernel module symbols. Integration is broad: PM72, PM81, PM91, PM112, PM121, RM31, and ancillary fan loops use these helpers.

## Risks And Test Signals
The functions trust `history_len` to be valid and nonzero; some callers clamp it, others depend on firmware data being sane. Fixed-point scaling and overflow boundaries are critical because gains and history sums use mixed 32/64-bit arithmetic. Test signals include first-sample history initialization, additive versus absolute targets, min/max clamping, large gain behavior, zero/oversized history protection by callers, and CPU PID response to rising temperature with falling or excessive power.
