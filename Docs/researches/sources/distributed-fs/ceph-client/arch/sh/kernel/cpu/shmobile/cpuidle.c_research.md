# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/shmobile/cpuidle.c

Purpose: registers SH-Mobile cpuidle states backed by the architecture standby/sleep implementation. It exposes regular sleep, sleep with RAM self-refresh, and software standby with self-refresh as cpuidle C-states.

Important APIs and control flow: `cpuidle_mode[]` maps cpuidle indexes to `SUSP_SH_*` mode flags. `cpuidle_sleep_enter()` bounds the requested state by an `allowed_mode`-derived state, calls `sh_mobile_call_standby(cpuidle_mode[k])`, and returns the state actually entered. `cpuidle_driver` describes C1/C2/C3 latencies, residency, names, and unusable defaults. `sh_mobile_setup_cpuidle()` enables C2/C3 based on `sh_mobile_sleep_supported` and calls `cpuidle_register()`.

State, dependencies, and risks: persistent state is only the registered cpuidle driver and mutable state flags. It depends on `pm.c`/`sleep.S` for actual standby execution and on platform self-refresh registration to set `sh_mobile_sleep_supported`. `allowed_mode` is currently hard-coded to `SUSP_SH_SLEEP`, so deeper states can be exposed but never selected by this function unless that policy changes. Test signals are platform boot, cpuidle sysfs visibility, and suspend/resume/idle residency validation on SH-Mobile hardware.
