
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kmem_cache_iter.c

## Purpose

`kmem_cache_iter.c` validates BPF iteration over kernel slab caches and open-coded kmem-cache iterator behavior.

## Important APIs, Types, and Functions

The test uses `kmem_cache_iter.skel.h`, `bpf_iter_create()`, reads from the iterator FD, compares against `/proc/slabinfo`, and directly runs `check_task_struct` and `open_coded_iter` programs with `bpf_prog_test_run_opts()`.

## Control Flow and Data Flow

After skeleton load/attach, it creates an iterator FD for `slab_info_collector` and drains it. Subtests verify the current task's `task_struct` belongs to a slab cache, compare BPF-collected slab names/object sizes against `/proc/slabinfo`, and run the open-coded iterator to ensure it sees the same number of caches as the explicit iterator.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the iterator link/FD, `slab_result` map, and BSS counters. Dependencies include kmem-cache iterator support, `/proc/slabinfo` availability, and stable enough slabinfo ordering during comparison. Integration is BPF iterator output and open-coded iterator parity. Risks are `/proc/slabinfo` absence, dynamic slab changes during comparison, and name truncation to 32 bytes. Test signals are `task_struct_found == 1`, BPF slab entries matching proc names/object sizes, read EOF after draining, and open-coded count equal to explicit count.
