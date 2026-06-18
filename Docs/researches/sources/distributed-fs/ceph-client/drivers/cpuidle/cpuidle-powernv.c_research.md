# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-powernv.c

Purpose: registers PowerNV cpuidle states from OPAL/platform idle descriptors, always including snooze and conditionally adding nap, fastsleep, and stop states with acceptable latency.

Important APIs and functions: `snooze_loop()` polls with low SMT priority until reschedule or timeout. `nap_loop()`, `fastsleep_loop()`, and `stop_loop()` enter PowerNV idle mechanisms via `power7_idle_type()` or `arch300_idle_type()`. `powernv_add_idle_states()` filters `pnv_idle_states` by supported flags, latency threshold, PSSCR validity, tick oneshot support, and timebase-stop behavior. `powernv_cpuidle_driver_init()` copies enabled states into the driver and sets `drv->cpumask = cpu_present_mask`. CPU hotplug callbacks enable/disable cpuidle devices.

Control flow and state: static state includes the driver, powernv state table, stop PSSCR table, max state count, snooze timeout configuration, and `cpuidle_state_table`. Probe only succeeds on OPAL firmware without idle override. Snooze timeout uses the next enabled state's target residency when possible.

Dependencies and integration points: depends on PowerNV OPAL firmware, `pnv_idle_states`, PSSCR stop metadata, timebase ticks, runlatch management, tick oneshot for timer-stop states, and CPU hotplug.

Risks and test signals: risks include filtering out high-latency firmware states, special handling when present CPUs differ from possible CPUs, conditional absence of timer-stop states without `CONFIG_TICK_ONESHOT`, snooze polling overhead, and platform firmware validity of stop states. Test signals include discovered states logged/visible under cpuidle sysfs, snooze timeout enabled when deeper states exist, stop states carrying expected PSSCR values, hotplug disable/enable transitions, and no registration when `cpuidle_disable` is set or OPAL is absent.
