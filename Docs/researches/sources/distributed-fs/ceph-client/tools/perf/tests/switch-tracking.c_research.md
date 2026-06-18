## sources/distributed-fs/ceph-client/tools/perf/tests/switch-tracking.c

Purpose: exclusive integration test for mixed tracking events, sched_switch system-wide events, and enabling/disabling sampled events.
Important types/functions: `struct switch_tracking`, `spin_sleep`, `check_comm`, `check_cpu`, `process_sample_event`, `process_event`, `add_event`, `process_events`, and `test__switch_tracking`.
Control flow: creates thread/CPU maps, parses cpu-clock/cycles, adds sched_switch, moves cycles to front, adds dummy tracking event, configures sampling, opens/mmaps, changes process comm four times while toggling cycles, then reads all mmap events sorted by timestamp.
State and persistence: `switch_tracking` tracks per-CPU current TIDs, seen COMM events, and whether cycles appeared before/between/after comm phases.
Dependencies and integration: evlist ordering/config, sched_switch fields `next_pid`/`prev_pid`, tracking COMM synthesis, sample time/CPU/id parsing, and PR_SET_NAME.
Risks: missing sched_switch support causes skip-like success; event ordering is reconstructed from timestamps and can fail if samples lack time.
Test signals: all four COMM events seen, no missing sched_switch transitions, cycles present only while enabled.
