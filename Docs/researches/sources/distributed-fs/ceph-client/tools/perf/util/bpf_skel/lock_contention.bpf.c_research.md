# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_contention.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/lock_contention.bpf.c

Purpose: this BPF program records kernel lock contention begin/end events, filters them, optionally captures call stacks and owner stacks, aggregates wait-time stats, identifies special lock classes, and exposes maps for user-space reporting.

Important maps and globals: maps include `stacks`, `stack_buf`, `owner_stacks`, `owner_data`, `owner_stat`, `tstamp`, `tstamp_cpu`, `lock_stat`, `task_data`, `lock_syms`, filter maps, `slab_filter`, `slab_caches`, and `lock_delays`. Ro/BSS globals configure filters, call stacks, owner tracing, cgroup mode, aggregation mode, stack skip/depth, delay injection, NUMA symbol addresses, and error counters.

Control flow: `contention_begin` checks filters, allocates a timestamp slot (per-CPU for spin-like locks, per-task otherwise), stores lock/timestamp/flags, captures waiter stack if requested, records task comms for task aggregation, and tracks owner stack state when owner tracing is enabled. `contention_end` finds the timestamp, computes duration, updates owner stats, builds a key based on caller/task/address/cgroup aggregation, creates or updates `lock_stat`, annotates special address locks, optionally delays, and clears/deletes timestamp state. Test-run programs collect runqueue/zone lock symbols and end timestamps. The slab iterator maps kmem_cache addresses to compact ids.

State and persistence: active contention state lives in `tstamp`/`tstamp_cpu`; aggregate stats in `lock_stat` and `owner_stat`; metadata in `task_data`, `lock_syms`, and `slab_caches`. Error counters persist for user-space diagnostics. `perf_subsys_id` is lazily initialized for cgroup v1.

Dependencies and integration: `bpf_lock_contention.c` sizes maps, populates filters, attaches programs, invokes test-run programs, reads stats, and decodes names. This BPF code depends heavily on CO-RE for mutex/rwsem/mm/rq/zone/cgroup layouts and optional kfuncs `bpf_get_kmem_cache`, `bpf_task_from_pid`, and `bpf_task_release`.

Risks: non-atomic max/min updates can race. Nested locks are intentionally skipped when a timestamp slot is already active. Owner stack tracing has many fallback paths and can lose attribution. `lock_delay` intentionally spins inside BPF and can perturb the system. Special lock identification depends on kernel symbols/layouts and may fail silently.

Test signals: run with callstack on/off, owner on/off, aggregation modes, filters, slab filters, and delay rules; inspect fail counters; validate special names (`mmap_lock`, `siglock`, `rq_lock`, `zone_lock`, slab names); and test kernels with missing optional BPF features.
