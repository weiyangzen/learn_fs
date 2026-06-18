# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_iter.c

## Purpose
This selftest is the broad regression harness for BPF iterator attachment, iterator file descriptors, bpffs-pinned iterator links, map-scoped iterators, task/socket/VMA iterators, and verifier rejection of invalid iterator programs. It validates both generic iterator mechanics and many target-specific iterator contracts by loading generated libbpf skeletons from `tools/testing/selftests/bpf/progs`.

## Important APIs, Types, And Functions
The file centers on `bpf_program__attach_iter()`, `bpf_iter_create()`, `bpf_link__pin()`, `bpf_link__update_program()`, `bpf_link_get_info_by_fd()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_get_info_by_fd()`, `sys_pidfd_open()`, `get_uprobe_offset()`, `kern_sync_rcu()`, and the skeleton APIs generated from the many included `bpf_iter_*.skel.h` headers. `union bpf_iter_link_info` and `struct bpf_iter_attach_opts` are used to scope iterators to task IDs, PID FDs, and particular maps.

## Control Flow
`test_bpf_iter()` initializes a mutex and dispatches dozens of subtests through `test__start_subtest()`. Common helpers attach an iterator program, create an iterator FD, drain it with `read()`, and destroy the link. Specialized paths check task selection by TID/PID/PIDFD, sleepable task access with a forked child, task stacks and files, BTF rendering of `task_struct`, TCP/UDP/UNIX socket iterators, anonymous and bpffs-pinned iterator links, seq-file overflow/restart behavior, map iterators for hash/array/per-CPU maps, socket local storage iteration and mutation, BPF link/ksym iterators, task VMA output versus `/proc/<pid>/maps`, dead-task VMA stability, sockmap iterator lifetime, and VMA offset calculation.

## State And Persistence Behavior
Most state is transient kernel object state held by skeleton BSS/data, iterator links, iterator FDs, maps, sockets, threads, child processes, and pinned bpffs paths. `test_file_iter()` persists an iterator link at `/sys/fs/bpf/bpf_iter_test1` long enough to validate file-based reads and link program replacement, then unlinks it. Map iterator lifetime tests deliberately destroy links and skeletons before draining iterator FDs to prove the iterator keeps required references alive across RCU grace periods.

## Dependencies And Integration Points
The test depends on libbpf skeleton generation, bpffs at `/sys/fs/bpf`, procfs maps, pthreads, fork/wait, kernel RCU synchronization helpers, pidfd support, socket APIs, BTF support, and the BPF selftest harness. It integrates with BPF program files such as `bpf_iter_tasks`, `bpf_iter_task_vmas`, `bpf_iter_bpf_hash_map`, `bpf_iter_bpf_sk_storage_map`, and `bpf_iter_sockmap`.

## Risks And Edge Cases
Risk concentrates around kernel-version-sensitive iterator targets, timing-sensitive thread/process counts, short-lived processes during VMA iteration, seq-file overflow semantics, and resource cleanup after early assertions. Several checks rely on expected verifier failures and exact errno values. The test mutates bpffs and opens many kernel resources, so cleanup of FDs, links, sockets, maps, child processes, and pinned paths is critical.

## Test Signals
Passing signals include successful skeleton loads and iterator attachment, nonnegative read termination, expected BSS counters, exact map value sums, expected `E2BIG`, `EACCES`, or load failures for invalid programs, matching first-line VMA output against `/proc/<pid>/maps`, stable link info, and successful reads after premature map/link closure.
