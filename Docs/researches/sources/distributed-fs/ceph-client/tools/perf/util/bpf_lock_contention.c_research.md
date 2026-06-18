# sources/distributed-fs/ceph-client/tools/perf/util/bpf_lock_contention.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_lock_contention.c

Purpose: this file is the user-space controller for BPF lock contention tracing. It configures filters and aggregation mode, resolves kernel symbols and slab/NUMA metadata, starts/stops BPF collection, accounts unfinished waits at stop time, converts BPF maps into perf `lock_stat` objects, and releases auxiliary state.

Important APIs and functions: `lock_contention_prepare()` is the central setup routine. It sizes maps, sets rodata for CPU/task/type/address/cgroup/slab filters, resolves symbol filters and delay injections, initializes BTF-dependent slab and NUMA data, loads and attaches the skeleton, populates filter maps, and optionally reads all cgroups. `lock_contention_start()`/`stop()` toggle `enabled`; `mark_end_timestamp()` uses `BPF_PROG_TEST_RUN` to capture a BPF timestamp; `account_end_timestamp()` accounts outstanding begin events; `lock_contention_read()` merges BPF `lock_stat` rows into perf's RB-tree stats; `pop_owner_stack_trace()` drains owner-stack rows; `lock_contention_finish()` destroys BPF and cgroup/BTF/slab state.

Control flow: preparation first loads the kernel map for symbol lookup, then configures maps according to `struct lock_contention`. CPU/task/type/address/cgroup/slab filters become BPF hash maps. Symbol names in filters and delay specifications are resolved to kernel addresses. Optional slab-cache iteration is enabled only when vmlinux BTF contains `bpf_iter__kmem_cache`. At read time, outstanding timestamps are converted to stats, address aggregation may test-run a BPF program to collect runqueue and zone lock symbols, and each BPF stat row is named according to aggregation mode.

State and persistence: the skeleton, slab-iterator availability, and slab cache hashmap are static. `con->btf` persists loaded vmlinux BTF until finish. BPF maps hold timestamps, per-CPU timestamps, stack traces, task comms, slab cache ids, lock symbol classes, owner stack data, delay settings, cgroup filters, and final contention stats. The perf-side global lock stat tree is updated via `lock_stat_find*`.

Dependencies and integration: it depends on perf machine/symbol/map APIs, cgroup helpers, target/thread maps, libbpf, vmlinux BTF, BPF kfunc availability for slab/owner stack features, and shared structs in `lock_data.h`. It integrates with `perf lock contention` aggregation by task, caller, address, or cgroup.

Risks: many features are kernel-version dependent: BTF, slab iterators, `bpf_get_kmem_cache`, `bpf_task_from_pid`, runqueue symbol layout, and zone layout. Some failures only reduce data quality counters. The file uses static state, so concurrent sessions can conflict. `lock_contention_prepare()` returns on load failure without destroying the opened skeleton. Address naming has two repeated `lock_syms` lookups and depends on flags encoding for special locks. Delay injection intentionally burns CPU and must be used carefully.

Test signals: test all aggregation modes, with and without call stacks and owner tracing; run on kernels with/without BTF slab iterator and cgroup v2; validate symbol/slab/name filters; check outstanding contention accounting after forced stop; compare fail counters; and run with small map sizes to exercise full-map paths.
