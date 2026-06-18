# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_iter_memcg.h

Purpose: shared query structure for cgroup memory iterator tests.

Important APIs and types: `struct memcg_query` contains selected memory cgroup node stats (`nr_anon_mapped`, `nr_shmem`, `nr_file_pages`, `nr_file_mapped`) and vm event `pgfault`.

Control flow: header only.

State and persistence: structure instances carry sampled memory counters between BPF/user-space test components.

Dependencies and integration points: included by cgroup iterator tests that need a stable ABI-like layout.

Risks: fields are a subset of kernel counters and depend on tests populating/interpreting them consistently; type widths assume unsigned long compatibility between sides.

Test signals: iterator tests can compare expected memory counter deltas in this structure.
