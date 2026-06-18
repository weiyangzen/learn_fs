# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/thuge-gen.c

Purpose: tests explicit hugepage size selection for `mmap(MAP_HUGETLB | MAP_HUGE_*)` and `shmget(SHM_HUGETLB | SHM_HUGE_*)` across available hugepage sizes.

Important APIs and functions: `find_pagesizes()` globs hugepage sysfs directories and checks free counts plus `shmmax`; `test_mmap()` maps, writes, and validates hugepage consumption; `test_shmget()` creates, attaches, writes, marks for removal, and validates consumption; `ilog2()` builds shift arguments.

Control flow and state: `main()` discovers usable sizes, sets a TAP plan, tests explicit/default mmap and shmget cases, and finishes. It temporarily consumes reserved hugetlb pages and creates SYSV shm segments marked `IPC_RMID`.

Dependencies and risks: depends on pre-reserved hugepages, sufficient `shmmax`, root for some shm behavior, `vm_util.h`, and kselftest. Parallel hugepage users can make free-page count assertions unstable.
