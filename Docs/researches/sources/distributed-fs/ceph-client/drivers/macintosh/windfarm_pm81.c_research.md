# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm81.c

## Purpose
Implements thermal control for first-generation iMac G5 systems (`PowerMac8,1` and `PowerMac8,2`). It controls system, drive-bay, and CPU fans using Darwin-derived PID tables and SMU SDB CPU calibration.

## Important APIs, Types, And Functions
System-loop parameters are represented by `wf_smu_sys_fans_param` and `wf_smu_sys_fans_state`; CPU-loop state by `wf_smu_cpu_fans_state`. Setup/tick functions are `wf_smu_create_sys_fans()`, `wf_smu_sys_fans_tick()`, `wf_smu_create_cpu_fans()`, `wf_smu_cpu_fans_tick()`, and `wf_smu_tick()`. Notifier callbacks `wf_smu_new_control()` and `wf_smu_new_sensor()` bind required Windfarm objects.

## Control Flow
Init reads the SMU sensor-tree model ID and registers only on PowerMac8,1/8,2. The notifier waits for `cpu-fan`, `system-fan`, `cpufreq-clamp`, optionally `drive-bay-fan`, plus `cpu-power`, `cpu-temp`, and `hd-temp`. First tick creates system and CPU loops. System fan ticks every five seconds from hard-drive temperature, scales one output for system fan, optionally drives the hard-drive fan directly, and cross-couples with the CPU target. CPU ticks every second from CPU temp/power and cross-couples with system target.

## State, Dependencies, And Integration
Persistent state includes model ID, sensor/control refs, PID state allocations, failure bits, readjust/skipping flags, and overtemp flag. It depends on Windfarm core and PID helpers, SMU SDB partitions (`SENSORTREE`, `CPUPIDDATA`, `FVT`), SMU/LM75 sensor providers, and cpufreq clamp.

## Risks And Test Signals
Removal uses a one-second delay due to notifier lifetime uncertainty and comments note possible sysfs/provider races. Model tables only cover IDs 2, 3, and 5, while init gates by machine compatible, so odd sensor-tree data can leave loops failed and fans maxed. Test signals include each model table path, missing drive fan on models greater than 3, SDB history clamping, overtemp notify/clear, readjust after failure recovery, and provider module unload behavior.
