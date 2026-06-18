# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm72.c

## Purpose
Implements thermal control for AGP PowerMac G5 `PowerMac7,2` and `PowerMac7,3` systems. It uses FCU fan controls, MPU EEPROM calibration, LM75/AD7417/MAX6690 sensors, and optional cpufreq clamp.

## Important APIs, Types, And Functions
Key routines are `read_one_cpu_vals()`, `cpu_setup_pid()`, `cpu_fans_tick_split()`, `cpu_fans_tick_combined()`, `cpu_check_overtemp()`, `backside_setup_pid()`, `backside_fan_tick()`, `drives_setup_pid()`, `drives_fan_tick()`, and `pm72_tick()`. Discovery callbacks bind `cpu-front-fan-N`, `cpu-rear-fan-N`, optional `cpu-pump-N`, `backside-fan`, `slots-fan`, `drive-bay-fan`, `cpufreq-clamp`, and CPU diode/voltage/current sensors.

## Control Flow
Init gates on PowerMac7,2/7,3, counts up to two CPU chips, requires MPU data for each, requests provider modules, and registers the Windfarm client. Once all required objects exist, the first tick initializes CPU PID loops from MPU fields, backside and drive PID loops, and fixes the slot fan to a default PWM. Systems with pumps switch to a combined liquid-cooling algorithm using the max temp/power across CPUs and scaled pump speed; otherwise each CPU is controlled separately with intake fan scaling.

## State, Dependencies, And Integration
State includes per-chip sensor/control arrays, MPU data pointers, CPU PID state, overtemp history, backside/drive PID state, topology flags, and failure bits. It depends on `wf_get_mpu()`, FCU controls, Windfarm PID helpers, OF machine and CPU-node enumeration, and `machine_power_off()`.

## Risks And Test Signals
Provider callbacks store raw pointers without `wf_get_*()` references, unlike newer SMU model drivers; unload races are mostly tolerated by platform assumptions. High overtemp powers off directly, and low overtemp/failure clamps cpufreq and maxes fans. Liquid-cooled pump calculations depend on valid MPU max exhaust RPM and pump controls. Test signals include one-chip/two-chip configurations, pump detection, MPU field sanity, split versus combined CPU control, backside U3 revision parameter selection, drive sensor failure, and cpufreq failure transitions.
