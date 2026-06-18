# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage_rcu_tasks_trace.c

Purpose: stresses task-local-storage destruction paths that use RCU Tasks Trace and measures grace-period latency and optional kthread CPU ticks while many sleeper processes exist.

Important APIs and functions: `--nr_procs` sets sleeper process count and `--kthread_pid` identifies `rcu_tasks_trace_kthread`. `local_storage_tasks_trace_setup()` forks sleepers with `PR_SET_PDEATHSIG`, loads `local_storage_rcu_tasks_trace_bench`, attaches `get_local`, `pregp_step`, and `postgp`. `kthread_pid_ticks()` parses `/proc/<pid>/stat` stime. `measure()` collects `gp_hits`, `gp_times`, and tick deltas. Reports use `grace_period_*_basic_stats()`.

Control flow: setup forks many children that sleep randomly and call `getpgid`; then the parent attaches BPF probes. The benchmark producer also triggers `getpgid` repeatedly. BPF-side probes measure RCU grace-period boundaries, and user-space sampling computes averages.

State and persistence: child processes persist for the benchmark lifetime and should die with the parent via PDEATHSIG. `ctx.prev_kthread_stime` maintains the previous tick sample. BSS counters are reset at each measurement.

Dependencies and integration points: depends on `local_storage_rcu_tasks_trace_bench.skel.h`, `bench.h`, `/proc`, `prctl`, process forking, and the presence of RCU Tasks Trace symbols/probes in the kernel.

Risks: very high `nr_procs` can exhaust PID/process resources; missing or wrong `kthread_pid` aborts; the parser for `/proc/<pid>/stat` is fragile to unexpected layout; a stray duplicated `break;` after argument parsing is harmless but untidy. If BPF sees post-GP before pre-GP, reporting exits because data is invalid.

Test signals: valid runs print average grace-period latency and ticks per grace period, unless quiet. Failure signals include fork/prctl errors, attach failures, and `unexpected` ordering in BPF BSS.
