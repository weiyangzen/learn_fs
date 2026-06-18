<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c

Purpose: validates per-CPU allocation support in BPF maps/local storage and userspace CPU-targeted map operation flags.

Important APIs and functions: `test_array()`, `test_array_sleepable()`, and `test_cgrp_local_storage()` load per-CPU allocation skeletons, set `my_pid` and `nr_cpus`, run selected programs, and check BSS aggregates (`cpu0_field_d`, `sum_field_c`). `test_failure()` runs verifier failures. `test_percpu_map_op_cpu_flag()` is a detailed userspace syscall test for `BPF_F_CPU` and `BPF_F_ALL_CPUS` on lookup/update/batch operations, including invalid combinations and `-ERANGE`. Wrapper helpers run this for percpu array/hash/LRU hash and percpu cgroup storage. `test_map_op_cpu_flag()` confirms CPU flags are rejected on non-percpu array/hash maps.

Control flow: top-level dispatches ten subtests covering BPF-side allocation, sleepable programs, cgroup storage, failure cases, percpu map CPU flags, and non-percpu rejection. The CPU-flag helper clears all CPUs, writes one CPU, checks per-CPU values, then repeats with batch APIs when supported.

State and persistence: cgroup setup, maps, per-CPU values, and BSS counters are transient. Cgroup environment is explicitly cleaned.

Dependencies and integration: depends on `percpu_alloc_array`, `percpu_alloc_cgrp_local_storage`, `percpu_alloc_fail` skeletons, libbpf possible-CPU count, cgroup helpers, and map batch syscalls.

Risks and test signals: correct BSS aggregates, verifier failures, per-CPU value isolation, and expected errors for invalid flags are signals. Risks include CPU count scaling, alignment/roundup expectations, and cgroup storage attachment cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/percpu_alloc.c -->
