<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c

## Purpose
`test_lru_dist.c` is a userspace stress and distribution test for BPF LRU hash maps. It compares kernel LRU map behavior against a perfect userspace LRU model, tests loss patterns, and exercises common and per-CPU LRU modes under parallel access.

## Important APIs, Types, And Functions
Core helpers are `pfect_lru_init()`, `pfect_lru_lookup_or_insert()`, `read_keys()`, `create_map()`, `sched_next_online()`, `run_parallel()`, `do_test_lru_dist()`, `test_parallel_lru_dist()`, `test_lru_loss0()`, `test_lru_loss1()`, `do_test_parallel_lru_loss()`, and `test_parallel_lru_loss()`. It uses `bpf_map_create()`, `bpf_map_lookup_elem()`, `bpf_map_update_elem()`, and BPF map flags including `BPF_F_NO_COMMON_LRU`.

## Control Flow
`main()` parses a key distribution file, LRU size, and task count, determines possible CPUs, and runs tests for common and per-CPU LRU maps. The perfect LRU uses a userspace hash map plus linked list to track ideal hits/misses. Parallel tests fork workers pinned across CPUs, execute the distribution, count map misses/unique entries, and print comparisons. Loss tests insert, touch, and evict key ranges to observe whether active entries survive.

## State And Persistence
Runtime state includes BPF map fds, per-process perfect-LRU nodes, loaded distribution keys, forked child processes, CPU affinity, and transient loss counters. No state persists after map fds close and memory is freed.

## Dependencies And Integration Points
It depends on libbpf syscall wrappers, CPU affinity APIs, fork/wait, input distribution files, and kernel BPF LRU hash map implementation. It integrates with BPF map semantics rather than loading any BPF program.

## Risks And Edge Cases
The test uses `assert()` heavily, so any syscall failure aborts. Parent and child share map fds across fork, which is intended but sensitive to process scheduling. Per-CPU LRU sizing differs from common LRU sizing. Input parsing reads the whole file into memory and assumes numeric lines.

## Test Signals
Useful output includes `nr_cpus`, loss counts for old/active/new ranges, per-task loss lines, and perfect-versus-kernel miss statistics. Stable active entries should show fewer losses than unused ranges, and both map flag modes should complete without assertion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_lru_dist.c -->
