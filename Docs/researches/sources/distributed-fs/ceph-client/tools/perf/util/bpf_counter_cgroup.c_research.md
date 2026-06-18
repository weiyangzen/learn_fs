# sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter_cgroup.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_counter_cgroup.c

Purpose: this file implements `bperf_cgrp_ops`, the BPF counter backend used when perf stat expands events across multiple cgroups. It opens one uncgrouped copy of each event per CPU, attaches a BPF program to cgroup-switch events, and aggregates deltas into per-cgroup/per-event maps.

Important APIs and functions: `setup_rodata()` sizes BPF maps and sets cgroup v1/v2 mode; `test_max_events_program_load()` validates verifier loadability for maximum configured events in debug builds; `bperf_load_program()` opens the skeleton, attaches `on_cgrp_switch` to `PERF_COUNT_SW_CGROUP_SWITCHES`, populates `events` and `cgrp_idx`, and checks raw tracepoint test-run support; `bperf_cgrp__enable()`, `bperf_cgrp__disable()`, and `bperf_cgrp__read()` synchronize counters and transfer `cgrp_readings` into perf counts.

Control flow: the first evsel load calls `bperf_load_program()` once via a static `bperf_loaded` flag. The code opens a software cgroup-switch event on all CPUs and attaches the BPF program to each fd. It then walks the evlist, opens a single non-cgroup instance for each leader cgroup group of events, installs fds into the BPF `events` perf-event array by event index and CPU, maps each cgroup id to an ordinal index, and later reads only from the first evsel invocation while iterating all evsels.

State and persistence: `skel` and `cgrp_switch` are static process-wide pointers. Map sizes depend on `nr_cgroups`, evlist entry count, and `cpu__max_cpu()`. BPF global `enabled` gates delta accumulation. The evsel's `follower_skel` is set to a casted non-null value solely to bypass `bpf_counter_skip()`, so it is a sentinel rather than a real follower skeleton.

Dependencies and integration: this code depends on cgroup id helpers, perf CPU maps, event opening, libbpf skeleton `bperf_cgroup`, and `bperf_trigger_reading()` from `bpf_counter.c`. It integrates with the cgroup-expanded evlist where entries are ordered by event and cgroup.

Risks: static global lifetime implies one cgroup BPF counter instance per process. `evlist_size % nr_cgroups` is enforced with `BUG_ON`, so malformed expansion is fatal. The read path allocates an array sized by `cpu__max_cpu().cpu`, which assumes CPU ids are bounded as expected. Missing cgroup ids are mapped to zero after a debug message, risking aggregation ambiguity. Kernel lack of test-run support only warns, so final reads may be less fresh.

Test signals: run `perf stat --for-each-cgroup ... --use-bpf` on cgroup v1 and v2 systems, with multiple events and CPUs; verify counts against normal cgroup perf; test unsupported/max-event verifier boundaries; and run cleanup under valgrind/ASAN to confirm the static skeleton and cgroup-switch evsel are released once.
