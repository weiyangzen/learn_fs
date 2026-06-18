# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/arena_spin_lock.c

Purpose: concurrency stress test for BPF arena spin locks under multiple userspace threads running the same BPF program on distinct CPUs.

Important APIs/types/functions: defines local qspinlock-compatible structs before including `arena_spin_lock.skel.h`. `spin_lock_thread` sets CPU affinity, synchronizes with a pthread barrier, and runs the BPF program repeatedly with `pkt_v4` as input. `test_arena_spin_lock_size` configures critical-section count/limit and verifies the final counter.

Control flow: each subtest chooses a lock-protected work size, opens/loads the skeleton, initializes a barrier for up to 16 threads or available CPUs, starts threads with increasing CPU affinity, joins them, handles skip flags, and asserts that the BPF counter equals `repeat * nthreads`. The top-level test runs sizes 1, 1000, and 50000 with adjusted repeat counts.

State and persistence behavior: global userspace `cpu`, `repeat`, and `barrier` coordinate threads. Skeleton BSS stores `cs_count`, `limit`, and final `counter`. Arena lock state is internal to the BPF program and reset per skeleton.

Dependencies and integration points: uses pthread barriers/affinity, `get_nprocs`, `network_helpers.h` packet fixture `pkt_v4`, and generated skeleton support.

Risks: requires at least two CPUs for useful coverage and may skip for unsupported kernel CPU count or arena spinlock support. CPU affinity can fail under restricted environments. Large critical-section size stresses timing.

Test signals: successful thread creation/join, test-run return values of zero or explicit unsupported skip, and final counter equality.
