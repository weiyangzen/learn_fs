# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm91.c

## Purpose
Implements Windfarm thermal control for the single-CPU desktop G5 `PowerMac9,1`. It manages CPU fan group, drive-bay fan, and slots fan using SMU sensors and PID loops.

## Important APIs, Types, And Functions
Important routines are `wf_smu_create_cpu_fans()`, `wf_smu_cpu_fans_tick()`, `wf_smu_create_drive_fans()`, `wf_smu_drive_fans_tick()`, `wf_smu_create_slots_fans()`, `wf_smu_slots_fans_tick()`, and `wf_smu_tick()`. The notifier binds `cpu-rear-fan-0`, `cpu-rear-fan-1` or `cpu-front-fan-0`, `drive-bay-fan`, `slots-fan`, `cpufreq-clamp`, and sensors `cpu-power`, `cpu-temp`, `hd-temp`, and `slots-power`.

## Control Flow
Init registers only on `PowerMac9,1` and requests SMU control/sensor, LM75, and clamp modules. First ready tick initializes drive, slots, and CPU loops. CPU PID uses SMU CPUPIDDATA and FVT partitions. Drive fan uses a five-second PID on hard-drive temperature, with additive mode depending on whether the control is RPM. Slots fan uses a one-second reset-only PID on slots power. Failures cause cpufreq clamp and all fans to max; recovery unclamps and forces readjust.

## State, Dependencies, And Integration
State includes sensor/control references, three allocated PID state objects, failure bits, readjust/skipping flags, and overtemp flag. It integrates with Windfarm notifiers, Windfarm PID helpers, SMU SDB partitions, and provider-created named controls.

## Risks And Test Signals
As with PM81, removal comments acknowledge notifier/sysfs lifetime races. CPU control requires one primary fan and at least one secondary/third fan; missing names prevent startup. Slots overtemp detection is disabled under `#if 0`, so slots power only affects fan speed. Test signals include SMU SDB absence, CPU secondary fan alternatives, drive control additive mode, slots-power sensor errors, cpufreq clamp transitions, and overtemp behavior from CPU or drive loops.
