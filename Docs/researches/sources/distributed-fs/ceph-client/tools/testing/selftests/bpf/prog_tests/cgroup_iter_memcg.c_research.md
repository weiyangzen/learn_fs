# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_iter_memcg.c

## Purpose
This test validates memory-cgroup iterator statistics by creating anonymous, file-backed, shared-memory, and page-fault activity and checking BPF-reported memcg counters.

## APIs, Types, and Functions
It uses `cgroup_iter_memcg.skel.h`, `cgroup_iter_memcg.h`, cgroup helpers, `bpf_program__attach_iter`, `bpf_iter_create`, `read`, `mmap`, file I/O, and the `struct memcg_query` shared with the BPF program. Helpers include `read_stats`, `test_anon`, `test_file`, `test_shmem`, and `test_pgfault`.

## Control Flow
The test joins a cgroup, loads the skeleton, attaches a memcg iterator link, and runs subtests that allocate/touch memory in different ways. After each activity, `read_stats` drains the iterator FD so the BPF program updates shared query fields, and assertions compare counters for anonymous memory, file cache, shmem, and page faults.

## State, Dependencies, and Integration
State includes cgroup membership, memory mappings, temporary file-backed pages, iterator link/FD, and BPF BSS query data. It depends on memcg accounting, mmap behavior, page cache updates, and cgroup iterator support.

## Risks and Test Signals
Signals are counter increases in expected categories. Risks include memory accounting races, kernel configuration differences for memcg, lazy page faulting, and noisy background memory activity in the test cgroup.
