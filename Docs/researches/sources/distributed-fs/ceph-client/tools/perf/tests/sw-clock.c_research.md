## sources/distributed-fs/ceph-client/tools/perf/tests/sw-clock.c

Purpose: verifies software clock sampling periods are meaningful under frequency mode and not all forced to period `1`.
Important functions: `__test__sw_clock_freq` and `test__sw_clock_freq`.
Control flow: builds an evlist with `PERF_TYPE_SOFTWARE` cpu-clock or task-clock, sample frequency 500, current TID map and any CPU map, opens/mmaps/enables it, spins for `NR_LOOPS`, disables, reads samples, sums `PERF_SAMPLE_PERIOD`, and fails if total periods equals sample count.
State and persistence: local evlist/evsel/cpu/thread maps and mmap buffers are cleaned.
Dependencies and integration: perf evlist/evsel APIs, mmap sample parsing, `/proc/sys/kernel/perf_event_max_sample_rate` hint.
Risks: insufficient samples or open/mmap permission failures return negative errors; tight spin duration may be system-sensitive.
Test signals: both CPU_CLOCK and TASK_CLOCK paths produce period sums not equal to all ones.
