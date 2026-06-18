<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c

## Purpose
`test_util.c` provides shared host and guest utility functions for KVM selftests. It covers SIGBUS handling, deterministic guest random numbers, size and integer parsing, `timespec` arithmetic, skip reporting, host backing-memory discovery, sysfs/procfs probing, and small string/clocksource helpers.

## Important APIs, Types, and Functions
Key APIs include `expect_sigbus_handler()`, `new_guest_random_state()`, `guest_random_u32()`, `parse_size()`, `timespec_to_ns()`, `timespec_add_ns()`, `timespec_add()`, `timespec_sub()`, `timespec_elapsed()`, `timespec_div()`, `print_skip()`, `thp_configured()`, `get_trans_hugepagesz()`, `is_numa_balancing_enabled()`, `get_def_hugetlb_pagesz()`, `vm_mem_backing_src_alias()`, `get_backing_src_pagesz()`, `is_backing_src_hugetlb()`, `backing_src_help()`, `parse_backing_src_type()`, `get_run_delay()`, `atoi_paranoid()`, `strdup_printf()`, and `sys_get_cur_clocksource()`. The backing source table maps `enum vm_mem_backing_src_type` values to names and mmap flags.

## Control Flow
Parsing functions validate input eagerly through `TEST_ASSERT()` and fail fast on overflow or trailing characters. Sysfs/procfs helpers stat or read files, returning booleans for optional kernel features and skipping when hugetlb is unavailable. Backing-source helpers centralize selection of anonymous, THP, hugetlb, shared memory, and explicit hugepage sizes. Time helpers convert through nanoseconds for consistent arithmetic.

## State and Persistence
State is limited to `expect_sigbus_jmpbuf` and transient heap allocations such as `strdup_printf()` and `sys_get_cur_clocksource()` results. The file reads host state from `/sys`, `/proc`, and clocksource files but does not persist changes.

## Dependencies and Integration Points
It depends on `test_util.h`, `linux/kernel.h`, libc file/stat/time APIs, `linux/mman.h`, and KVM selftest assertion/skip conventions. The backing source helpers are used by VM memory region creation and stress tests, while the time helpers are used by performance and timer tests.

## Risks and Test Signals
Risks include misparsing large sizes, assuming sysfs/procfs file formats, using default hugepage size when no pool exists, and returning stale or malformed clocksource strings. Test signals are `TEST_ASSERT()` failures, `KSFT_SKIP` exits for unavailable host features, and performance output that depends on sane `timespec` arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/test_util.c -->
