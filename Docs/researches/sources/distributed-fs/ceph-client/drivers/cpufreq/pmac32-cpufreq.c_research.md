# sources/distributed-fs/ceph-client/drivers/cpufreq/pmac32-cpufreq.c

## Purpose

`pmac32-cpufreq.c` provides 32-bit PowerMac CPUFreq support for older Apple PowerBook/iBook/MacRISC3 systems. It exposes two firmware-defined speeds, high and low, and selects one of several machine-specific mechanisms: PMU command plus sleep transition, GPIO bus slewing, 7447A DFS, or 750FX PLL control.

## Important APIs, types, and functions

- Global frequency state includes `low_freq`, `hi_freq`, `cur_freq`, `sleep_freq`, and `transition_latency`.
- `set_speed_proc` and `get_speed_proc` point to the selected hardware implementation.
- `cpu_750fx_cpu_speed()`, `dfs_set_cpu_speed()`, `gpios_set_cpu_speed()`, and `pmu_set_cpu_speed()` implement the four transition mechanisms.
- `do_set_cpu_speed()` wraps transitions and temporarily disables/restores L3 cache around low-speed changes.
- `pmac_cpufreq_suspend()` and `pmac_cpufreq_resume()` force safe speed/voltage handling across sleep.
- `pmac_cpufreq_init_MacRISC3()`, `pmac_cpufreq_init_7447A()`, and `pmac_cpufreq_init_750FX()` detect machine-specific data from device tree.
- `pmac_cpufreq_setup()` is module init and registers the cpufreq driver after selecting a transition implementation.

## Control flow

Setup exits early if the boot command line contains `nocpufreq`. It reads CPU0 `clock-frequency`, then checks machine compatibles and CPU PVR to pick a backend. MacRISC3 systems may use voltage/frequency/slew GPIOs derived from KeyLargo-style device-tree nodes, or PMU-based min/max clock properties. 7447A systems use dynamic power step and DFS with voltage GPIO. 750FX systems use reduced-clock-frequency and HID/PLL control.

The cpufreq table has only high and low entries. A target call passes the selected table index to `do_set_cpu_speed()`, which calls the selected backend and updates `cur_freq` and `ppc_proc_freq`. PMU-based transitions are the most invasive: they suspend PMU operations, raise MPIC priority, suppress decrementer interrupts, disable interrupts, save cache control registers, issue a PMU speed command, enter low-level sleep handling, restore northbridge/cache/MMU context, and resume PMU.

## State and persistence behavior

The driver uses global state because supported systems have one CPU frequency domain. Hardware speed persists in GPIOs, HID/DFS/PLL bits, or PMU-selected PLL configuration. Suspend stores `sleep_freq`, forces high speed for non-PMU low-speed sleep, and resume restores the previous high/low choice after re-reading speed when possible. `no_schedule` switches delays from sleepable `msleep()` to `mdelay()` during suspend.

## Dependencies

Dependencies include PowerMac feature calls, PMU/ADB infrastructure, Open Firmware properties, KeyLargo GPIO addressing, Book3S low-level assembly helpers (`low_choose_7447a_dfs`, `low_choose_750fx_pll`, `low_sleep_handler`), MPIC, PowerPC cache/MMU helpers, and `ppc_proc_freq`.

## Risks and edge cases

- The file itself notes it needs cleanup; many machine detections and transition styles share one global driver.
- Device-tree frequency data is known to be wrong on some machines, so the code contains model-specific corrections.
- PMU transitions run with interrupts suppressed and manipulate cache/MMU/decrementer state; failures can be catastrophic.
- GPIO address extraction is described as hackish and assumes KeyLargo register layout.
- The driver does not provide module exit/unregister in this file, so it is effectively init/lifetime bound.

## Test signals

Validation requires real supported PowerMac hardware. Signals include correct high/low table values, successful backend detection, repeated high/low transitions, voltage GPIO sequencing before up and after down transitions, DFS/PLL state reads matching `get_speed_proc`, suspend/resume restoring prior speed, and no clock/decrementer/cache corruption after PMU sleep transitions.
