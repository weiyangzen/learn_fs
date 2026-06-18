<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c

## Purpose

Provides cpufreq support for IBM/OpenPOWER bare-metal PowerNV systems using OPAL firmware P-state descriptions and POWER PMCR/PMSR special-purpose registers. It also tracks OCC throttling and POWER8 global-pstate ramp-down behavior.

## APIs, Types, And Functions

Global firmware data is held in `powernv_freqs`, `pstate_revmap`, and `powernv_pstate_info`. `struct global_pstate_info` tracks timer-based global pstate ramp-down per policy, while `struct chip` tracks per-chip throttle state and work. Main cpufreq callbacks are `powernv_cpufreq_cpu_init()`, `powernv_cpufreq_target_index()`, `powernv_fast_switch()`, `powernv_cpufreq_get()`, and `powernv_cpufreq_cpu_exit()`. Initialization uses `init_powernv_pstates()` and `init_chip_info()`.

## Control Flow

Module init requires OPAL firmware, reads `/ibm,opal/power-mgt` pstate min/max/nominal/turbo properties, builds the cpufreq table and reverse map, creates chip masks, enables software boost for WOF platforms, registers cpufreq, then registers reboot and OPAL OCC notifiers. Targeting converts table index to local/global pstate ids, checks throttling, optionally updates POWER8 global pstate ramp-down state, and sends `set_pstate()` to one CPU in the policy. Fast switch writes PMCR directly for the current CPU.

## State And Persistence

Persistent hardware state is PMCR/PMSR local, global, and max pstate fields. Software state includes global throttle booleans, per-chip counters exposed in sysfs `throttle_stats`, per-policy timers, reverse-map hashtable entries, and notifier registrations. Reboot notifier forces nominal pstate and suppresses non-nominal requests. Exit unregisters cpufreq/notifiers and cancels chip work.

## Dependencies And Integration Points

Depends on OPAL device-tree properties, firmware feature checks, PowerPC SPR access, OPAL OCC messages, reboot notifiers, sysfs cpufreq attributes, CPU/thread topology, and tracepoint `powernv_throttle`.

## Risks And Test Signals

Risks include invalid firmware pstate tables, stale reverse-map defaults to nominal, timer migration races, OCC throttle restoration, and fast-switch bypass of cached global pstate state. Test signals include pstate table logs, `cpuinfo_nominal_freq`, throttle stat counters, trace events on Pmax changes, PMCR/PMSR readback, reboot nominal transition, and POWER8 timer ramp-down behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c -->
