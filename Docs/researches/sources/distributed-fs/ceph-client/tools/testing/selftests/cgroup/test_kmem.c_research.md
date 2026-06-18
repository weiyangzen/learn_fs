# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kmem.c

## Purpose

`test_kmem.c` validates memory cgroup kernel-memory accounting for slab/dcache, deleted memcgs, `/proc/kpagecgroup`, kernel stacks, dying descendants, and percpu memory. The complete 458-line file was read.

## Important APIs, Types, and Functions

Key constants are `MAX_VMSTAT_ERROR` and `KMEM_DEAD_WAIT_RETRIES`. Helpers include `alloc_dcache()`, `alloc_kmem_smp()`, `cg_run_in_subcgroups()`, `spawn_1000_threads()`, and tests `test_kmem_basic()`, `test_kmem_memcg_deletion()`, `test_kmem_proc_kpagecgroup()`, `test_kmem_kernel_stacks()`, `test_kmem_dead_cgroups()`, and `test_percpu_basic()`.

## Control Flow

`main()` finds cgroup v2, verifies the memory controller, enables it, then runs six tests. Tests allocate negative dentries, force reclaim with `memory.high`, create/destroy many child memcgs under a memory-enabled parent, read all of `/proc/kpagecgroup`, spawn 1000 threads to validate `kernel_stack`, poll `nr_dying_descendants`, and compare parent `memory.current` to stat components.

## State and Persistence Behavior

It creates many memory cgroups, charges kernel slab/percpu/thread stack memory, sets `memory.high`, reads memory stats, and destroys subtrees. State is transient but can rely on asynchronous RCU and rstat cleanup.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller, `memory.stat`, `memory.current`, `memory.high`, `cgroup.stat`, `/proc/kpagecgroup`, pthreads, `get_nprocs()`, and `cgroup_util`.

## Risks and Edge Cases

Accounting is approximate because per-cpu batches and asynchronous freeing create lag. Large thread counts and 1000 cgroups can stress small systems. `/proc/kpagecgroup` may require privileges or kernel config. Fixed waits for RCU/dying cgroups can be too short on busy hosts.

## Test Signals

Expected signals include slab growth above 1MB then reclaim below half, parent current matching anon+file+kernel+sock within `MAX_VMSTAT_ERROR`, full `/proc/kpagecgroup` read to EOF, `kernel_stack` at least 1000 pages, `nr_dying_descendants` eventually zero, and percpu accounting close to `memory.current`.
