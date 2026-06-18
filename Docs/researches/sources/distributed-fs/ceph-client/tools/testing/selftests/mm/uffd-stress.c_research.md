<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c

## Purpose
Stress test for userfaultfd that repeatedly transfers physical memory between source and destination mappings using UFFD fault resolution. It targets concurrency races among faulting mutator threads, UFFD handler threads, and background copy threads over anonymous, shmem, and hugetlb mappings.

## Important APIs, Types, and Functions
- `locking_thread()` randomly or sequentially locks per-page mutexes in `area_dst`, verifies counters, and increments them.
- `uffd_read_thread()` handles blocking-read UFFD mode; `uffd_poll_thread()` from `uffd-common.c` handles poll mode.
- `background_thread()` copies each CPU shard, optionally enabling write protection midway.
- `stress()` creates and joins locking, UFFD, and background workers for one bounce.
- `userfaultfd_stress()` registers ranges, runs bounces, unregisters, verifies counters, swaps source/destination pointers, and reports stats.
- `set_test_type()` and `parse_test_type_arg()` select anonymous, shmem, shmem-private, hugetlb, or hugetlb-private modes and negotiate UFFD features.

## Control Flow
`main()` parses `<test type> <MiB> <bounces>`, arms SIGALRM, computes CPU parallelism capped at 32, validates hugetlb availability, and calls `userfaultfd_stress()`. Each bounce toggles mode bits derived from the decreasing `bounces` counter, sets blocking or nonblocking fd flags, registers destination and alias ranges, drops destination pages, runs worker threads, clears WP if active, unregisters ranges, optionally verifies all counters, swaps mappings, and prints fault totals.

## State and Persistence Behavior
State is held in a heap-allocated global `gopts`, `features`, `bounces`, `zeropage`, and pthread attributes. SIGALRM periodically toggles `test_uffdio_copy_eexist` so copy retry paths are exercised. No durable files are created, but the test consumes hugepage reservations when hugetlb mode is used and heavily mutates VMAs with UFFD ioctls and `madvise`.

## Dependencies and Integration Points
Depends on `uffd-common.h`, `vm_util.c` helpers, UFFD kernel features, `getrandom()`, pthreads, signals, kselftest exit codes, and system hugepage availability. It is built as the `uffd-stress` selftest program and run with explicit test type/size/bounce arguments.

## Risks and Edge Cases
The test deliberately creates races and depends on faulting through `pthread_mutex_lock()`. Too-small memory sizes yield zero pages per CPU and abort. High CPU counts are capped to avoid zero shard size. Hugetlb tests skip when insufficient free hugepages exist. Kernel privilege restrictions on userfaultfd can skip or fail setup.

## Test Signals
Success is process exit 0 after all bounces. Failures are hard exits on memory corruption, unexpected write faults, bad UFFD event/ioctl behavior, worker creation/join errors, or unregister failures. Hugetlb shortage prints a skip message and returns `KSFT_SKIP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-stress.c -->
