# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_hugetlb_memcg.c

## Purpose

`test_hugetlb_memcg.c` validates memory cgroup accounting for hugetlb pages when the cgroup mount has `memory_hugetlb_accounting`. The complete 234-line file was read.

## Important APIs, Types, and Functions

Key constants are `ADDR`, `FLAGS`, `LENGTH`, and `PROTECTION`. Helpers include `get_hugepage_size()`, `set_file()`, `set_nr_hugepages()`, `check_first()`, `write_data()`, `hugetlb_test_program()`, and `test_hugetlb_memcg()`.

## Control Flow

`main()` checks the mount option, requires 2MB hugepages, finds cgroup v2, then runs one test. The child test sets `nr_hugepages`, mmaps 8MB of hugetlb memory, verifies mmap alone does not charge memory, reads one page and expects about 2MB charged, writes the full range and expects about 8MB charged, unmaps, and expects usage to return to baseline.

## State and Persistence Behavior

It writes `/proc/sys/vm/nr_hugepages`, creates a cgroup with `memory.max=100M` and `memory.swap.max=0`, maps hugetlb pages, faults them, and observes `memory.current`. The hugepage count is not restored by this file.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller, hugetlb support, 2MB hugepages, `/proc/meminfo`, `/proc/sys/vm/nr_hugepages`, `mmap(MAP_HUGETLB)`, and `cgroup_util`.

## Risks and Edge Cases

Systems without the mount option, without 2MB hugepages, or without permission to set `nr_hugepages` skip or fail. Global hugepage pool changes can affect other workloads. The fixed expected 2MB charge is specific to default hugepage size.

## Test Signals

Pass requires no charge for pool setup or mmap, approximate 2MB charge after first fault, approximate 8MB after touching all pages, and usage dropping back after `munmap()`.
