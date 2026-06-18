<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c

## Purpose

Implements CPU frequency scaling for 970FX/SMU based PowerMac G5 systems. It supports two operating points, high and low, using either SCOM register programming on SMU-era Neo2 systems or PowerMac platform functions on PowerMac7,2/7,3 and RackMac3,1.

## APIs, Types, And Functions

The cpufreq core entry points are `g5_cpufreq_cpu_init()`, `g5_cpufreq_target()`, and `g5_cpufreq_get_speed()` in `g5_cpufreq_driver`. Hardware-facing callbacks are selected through global function pointers `g5_switch_volt`, `g5_switch_freq`, and `g5_query_freq`. The SCOM path uses `g5_scom_switch_freq()` and `g5_scom_query_freq()` with PCR/PSR bitfields. The platform-function path uses `g5_pfunc_switch_freq()`, `g5_pfunc_switch_volt()`, and lookup of `pmf_function` handles.

## Control Flow

`g5_cpufreq_init()` locates CPU0's OF node and dispatches by machine compatible. Neo2 initialization validates CPU version, reads `power-mode-data`, discovers SMU FVT or VD-NAP platform functions, computes high/low frequencies from `clock-frequency`, synchronizes voltage and current mode, then registers the driver. PM72 initialization discovers the cpuid EEPROM and i2c clock node, resolves get/set/slewing platform functions, computes the low frequency from EEPROM ratios, synchronizes state, and registers.

## State And Persistence

Global state holds the two-entry `g5_cpu_freqs`, current mode `g5_pmode_cur`, OF-provided power mode data, SMU FVT data, and retained platform-function handles. The persistent hardware state is voltage and CPU clock mode in SMU/SCOM or i2c/platform-function controlled devices. `ppc_proc_freq` is updated after transitions. There is no unregister/remove path beyond module init registration.

## Dependencies And Integration Points

Depends on Open Firmware machine compatibles, PowerMac platform functions, SMU simple commands, `scom970_read/write`, PowerPC `ppc_proc_freq`, and the cpufreq table API. Integration is restricted to supported G5 machine families and CPU0-derived policy.

## Risks And Test Signals

Transition ordering is critical: voltage is raised before increasing frequency and lowered after decreasing frequency. Slewing wait loops poll for at most about 100 ms and only warn on timeout, so incomplete hardware transitions can still update software state. Test signals include boot logs naming frequency/voltage methods, correct high/low rates, SCOM PSR readback, platform-function slewing completion, and stable operation across repeated target changes and suspend/resume-style firmware state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c -->
