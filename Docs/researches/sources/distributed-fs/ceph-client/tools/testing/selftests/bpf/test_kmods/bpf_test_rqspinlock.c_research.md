# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/bpf_test_rqspinlock.c

## Research

This kernel module stress-tests `rqspinlock_t` behavior under normal thread context and NMI/perf-event context. It creates worker kthreads, pinned hardware perf events, and per-CPU histograms to exercise nested lock acquisition patterns.

Important state includes three rqspinlocks, module parameters `test_mode`, `normal_delay`, and `nmi_delay`, per-CPU `rqsl_cpu_hist`, arrays of perf events and kthreads, readiness counters, and a pause flag. Modes choose lock ordering: `AA`, `ABBA`, or `ABBCCA`. `rqsl_get_lock_pair()` maps each CPU and mode to worker/NMI lock choices. `rqspinlock_worker_fn()` repeatedly acquires worker-side locks, delays, and records success/failure latency. Perf event overflow/NMI handling acquires the paired lock and records NMI-context results.

Init allocates per-CPU perf events, starts worker threads, waits for readiness, enables events, and reports configuration. Exit pauses workers, disables/frees perf events, stops threads, prints latency histograms, and releases allocated arrays. State is entirely kernel runtime state; no files are persisted.

Dependencies are architecture support for `asm/rqspinlock.h`, perf hardware cycle events, kthreads, SMP, atomics, and module parameters. Risks include hardware perf unavailability, long delays causing slow tests, CPU hotplug assumptions, and contention patterns that can expose hangs or soft lockups if rqspinlock is broken. Test signals are successful module load/unload, no deadlock, populated success/failure counters, and printed histograms with slow-bucket visibility.
