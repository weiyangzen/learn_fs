# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_pm112.c

## Purpose
Implements the Windfarm thermal-control client for dual-core desktop PowerMac11,2 G5 systems with SMU and PPC970MP processors. It coordinates per-core CPU fan control, backside/U4, PCI slots, drive bay, overtemperature handling, and optional cpufreq clamping.

## Important APIs, Types, And Functions
Core routines include `create_cpu_loop()`, `cpu_fans_tick()`, `cpu_check_overtemp()`, `backside_fan_tick()`, `slots_fan_tick()`, `drive_bay_fan_tick()`, `set_fail_state()`, and `pm112_tick()`. Discovery callbacks `pm112_new_control()` and `pm112_new_sensor()` bind named Windfarm objects. The platform driver registers a notifier block on the shared `"windfarm"` platform device.

## Control Flow
Init gates on `PowerMac11,2`, counts CPU cores, requests provider modules when built as a module, and registers the platform driver. The notifier accumulates required controls and sensors. Once ready, each tick lazily creates CPU PID state from SMU SAT FVT/PID partitions, then reads every core's `cpu-temp-N` and `cpu-power-N`, chooses the target from the core with greatest thermal delta, limits fan decreases to 20 RPM per tick, scales pump/inlet fan outputs, and runs ancillary loops at their configured intervals.

## State, Dependencies, And Integration
Persistent state includes arrays of per-core sensors, CPU fan controls, CPU PID states, 180-second maximum-temperature history, ancillary PID state, fan scaling, readiness flags, and failure bits. It depends on SMU SAT partitions via `smu_sat_get_sdb_partition()`, Windfarm PID helpers, Windfarm control/sensor reference APIs, OF machine matching, and `machine_power_off()`.

## Risks And Test Signals
The driver assumes exact provider names and can wait forever if a required object never registers. High overtemperature powers off immediately; low overtemperature ramps fans and blocks normal control until cleared. History initialization starts from zero rather than first sample, so early average calculations are conservative in a different way than PM72/RM31. Test signals include missing SAT partitions, per-core sensor failures, fan set failures, pump scale calculations, cpufreq clamp transitions, and overtemperature immediate/average paths.
