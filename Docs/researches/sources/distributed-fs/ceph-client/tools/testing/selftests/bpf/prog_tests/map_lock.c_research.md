<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c

Purpose: stresses `BPF_F_LOCK` map operations and BPF spin-lock consistency under concurrent BPF program execution and userspace map reads.

Important APIs and functions: `spin_lock_thread()` repeatedly runs a cgroup skb program 10,000 times through `bpf_prog_test_run_opts()`. `parallel_map_access()` reads map values with `bpf_map_lookup_elem_flags(..., BPF_F_LOCK)` and checks that protected fields are internally consistent. `test_map_lock()` loads `test_map_lock.bpf.o`, finds `hash_map` and `array_map`, seeds the hash map, starts four BPF runner threads and two userspace reader threads, and joins them.

Control flow: load object, get map fds, seed map, run six threads, validate joins, close object.

State and persistence: map elements are mutated by BPF programs and observed by userspace under lock. All fds are transient.

Dependencies and integration: depends on pthreads, `test_map_lock.bpf.o`, cgroup skb test-run support, and lockable map values.

Risks and test signals: consistent arrays in 10,000 reads and zero BPF retval failures are signals. Risks are nondeterministic race failures, scheduling load, and lock ABI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_lock.c -->
