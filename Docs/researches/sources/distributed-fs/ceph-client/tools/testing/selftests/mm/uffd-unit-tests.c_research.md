<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c

## Purpose
Feature-matrix unit test driver for userfaultfd. It validates API negotiation, registration ioctl availability, zeropage, move, write-protect fork semantics, minor faults, signal delivery, non-cooperative events, poison, mmap-changing races, and backend-specific behavior across anonymous, shmem, shmem-private, hugetlb, and hugetlb-private memory.

## Important APIs, Types, and Functions
- `mem_type_t` maps memory names to backend flags, `uffd_test_ops`, and shared/private mode.
- `uffd_test_case_t` defines the unit-test table: name, function, target memory mask, required UFFD feature bits, and optional allocation hooks.
- `test_uffd_api()` validates syscall and `/dev/userfaultfd` API negotiation, bad API rejection, bad feature rejection, and double-initialization rejection.
- WP/fork coverage is in `uffd_wp_unpopulated_test()`, `uffd_wp_fork_test_common()`, and `uffd_wp_fork_pin_test_common()`.
- Minor-fault coverage is in `uffd_minor_test_common()`.
- Event/signal coverage is in `faulting_process()`, `uffd_sigbus_test_common()`, and `uffd_events_test_common()`.
- Zeropage, poison, and move coverage live in `uffd_zeropage_test()`, `uffd_poison_test()`, and `uffd_move_test_common()`.
- `uffd_mmap_changing_test()` validates ioctl behavior while a mmap-changing event is pending.

## Control Flow
`main()` parses `-f`, `-l`, and `-h`. Unless listing/filtering only, it first checks UFFD availability via both syscall and device paths. It then iterates tests and memory backends, filters unsupported backend/test combinations, checks feature bits via `uffd_get_features()`, initializes a one-thread UFFD test context, executes the test function, and clears the context. The test table is the authoritative control surface for coverage and feature gating.

## State and Persistence Behavior
All state is per-process: `gopts`, counters, UFFD fds, mappings, pagemap fds, gup_test fd state, signal jump buffer, and child process fds from `UFFD_EVENT_FORK`. Tests may interact with `/proc/self/pagemap`, `/sys/kernel/debug/gup_test`, and forked children. They do not intentionally persist files, but they rely on kernel debugfs and VM state.

## Dependencies and Integration Points
Depends on `uffd-common.h`, `vm_util.h`, `kselftest.h`, Linux `gup_test.h`, UFFD feature flags, `/proc/self/pagemap`, debugfs `gup_test`, pthreads, fork/wait, signals, and `madvise` behavior. It integrates with kselftest by manually maintaining pass/skip/fail counters and returning `KSFT_PASS` or `KSFT_FAIL`.

## Risks and Edge Cases
Feature gating is critical because many tests require newer UFFD features such as MOVE, POISON, WP_UNPOPULATED, EVENT_FORK, EVENT_REMAP, EVENT_REMOVE, and minor fault support. GUP pin tests skip if debugfs support or privilege is missing. Some paths intentionally rely on swap/pageout behavior, PMD collapse, or hugetlb limitations and may skip when unavailable. Error-injection tests expect exact errno/result-field behavior.

## Test Signals
The final line reports pass/skip/fail counts. Individual tests print `Testing <case> on <mem>... done`, `skipped`, or `failed`. Hard errors use `err()` for impossible internal states. The process returns fail if any kselftest failure counter is nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-unit-tests.c -->
