# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rps.c Research

Purpose: this suite validates Render Power States frequency control, clock interval conversion, command-streamer frequency scaling, SRM-based frequency observation, PM interrupt generation, power reduction at lower frequency, and dynamic reclocking.

Important APIs/types/functions: exported subtests are `live_rps_clock_interval()`, `live_rps_control()`, `live_rps_frequency_cs()`, `live_rps_frequency_srm()`, `live_rps_interrupt()`, `live_rps_power()`, and `live_rps_dynamic()`. Helpers include `create_spin_counter()`, `wait_for_freq()`, `rps_set_check()`, `measure_frequency_at()`, `measure_cs_frequency_at()`, `scaled_within()`, interrupt probes `__rps_up_interrupt()` / `__rps_down_interrupt()`, and RAPL power measurement helpers.

Control flow: most tests idle the GT, replace `rps->work.func` with `dummy_rps_work` to suppress normal reclocking work, disable heartbeats around spinners, then drive engines busy or idle while programming frequencies. Clock interval tests program RPS evaluation interval registers and compare GT clock conversion to wall time. Frequency tests run a command-streamer counter loop and compare counts at min/max RPS. Interrupt tests force min/max, sleep for evaluation intervals, and inspect `pm_iir`. Dynamic tests start from min, run a spinner, and expect frequency to rise and later fall.

State and persistence: this file actively changes RPS requested frequencies, `rps->work.func`, RC6 state, PM interrupt enable/disable, forcewake registers, PM QoS latency requests, engine heartbeat state, CS GPRs, and spinner batches. Cleanup restores work function, removes PM QoS requests, ends spinners, re-enables RC6/heartbeats, and flushes tests.

Dependencies/integration: it integrates with RPS/RP registers, GT clock utilities, engine PM, RC6, librapl, PM QoS, command streamer MI math/SRM commands, pcode frequency tables, and performance-limit reason registers. The header exports these functions for selftest registration.

Risks and test signals: platform firmware throttling, C-state latency, RAPL availability, fragile PCU behavior, and timing jitter can affect results. Some scaling mismatches are logged as `-EINTR` to continue probing. Strong pass signals are requested frequencies being reached, clock intervals within 80-125% tolerance, command counters scaling with frequency, UP/DOWN PM interrupts recorded without unexpected frequency changes, lower-frequency power saving, and dynamic busy/idle reclocking.
