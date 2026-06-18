# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_rm31.c

## Purpose
Implements thermal control for Xserve G5 `RackMac3,1`. It handles per-chip triple CPU fans, backside fan, slots fan, DIMM temperature clamping, MPU-calibrated CPU PID loops, and cpufreq failure clamping.

## Important APIs, Types, And Functions
Key functions include `read_one_cpu_vals()`, `cpu_setup_pid()`, `cpu_fans_tick()`, `cpu_check_overtemp()`, `backside_setup_pid()`, `backside_fan_tick()`, `slots_setup_pid()`, `slots_fan_tick()`, and `rm31_tick()`. Discovery callbacks bind `cpu-fan-a/b/c-N`, `backside-fan`, `slots-fan`, `cpufreq-clamp`, CPU diode/voltage/current sensors, `backside-temp`, `slots-temp`, and `dimms-temp`.

## Control Flow
Init gates on `RackMac3,1`, counts up to two CPU chips, requires MPU data, requests FCU and sensor provider modules, and registers the Windfarm client. The first ready tick initializes CPU PID state from MPU EEPROM plus backside, DIMM, and slots PID loops. Each tick runs backside/DIMM and slots loops before CPU loops so DIMM output can clamp CPU fan speed. CPU control reads temp/voltage/current, computes power, checks overtemp, runs per-chip CPU PID, then applies the max of CPU target and DIMM clamp to all three fans for that CPU.

## State, Dependencies, And Integration
State includes two-chip arrays of sensors and fan controls, MPU data, CPU PID state, 180-second CPU temperature history, backside/slots/DIMM PID states, `dimms_output_clamp`, readiness flags, and failure bits. It depends on FCU controls, LM75/LM87/AD7417/MAX6690 sensors, Windfarm PID, OF machine matching, and `machine_power_off()`.

## Risks And Test Signals
The driver stores raw provider pointers without reference acquisition and relies on platform/module assumptions. DIMM PID output is in RPM-like units and is converted into backside percentage minimum as well as CPU clamp, so scaling mistakes affect multiple loops. Test signals include one/two-chip Xserve layouts, LM87 `dimms-temp` discovery, DIMM clamp propagation, slots/backside PID min/max clamping, high-overtemp poweroff, and fan/sensor failure max-fan behavior.
