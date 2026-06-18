# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_fault_after_madv.c

## Purpose
`hugetlb_fault_after_madv.c` is a race regression test for faults against a hugetlb page while another thread repeatedly applies `MADV_DONTNEED`.

## Important APIs, types, and functions
Global state includes `huge_ptr`, `huge_page_size`, a `sigjmp_buf`, and `sigbus_triggered`. `signal_handler()` catches `SIGBUS`. `touch()` repeatedly writes to the hugepage with longjmp recovery, while `madv()` repeatedly calls `madvise(MADV_DONTNEED)`.

## Control flow
`main()` installs a SIGBUS handler, requires exactly one free hugepage, then loops up to 10,000 times. Each iteration maps one anonymous hugetlb page, starts the madvise and touch threads, waits for both, and unmaps. It reports one kselftest result asserting no SIGBUS occurred.

## State and persistence behavior
The test repeatedly allocates and releases the sole available hugepage while racing reservation/free and write faults. The required initial state is exactly one free hugepage.

## Dependencies and integration points
Depends on pthreads, signals, hugetlb support, and `vm_util.h` for hugepage size/free counts. It should be run in an isolated hugepage pool.

## Risks and edge cases
The exact-one-hugepage precondition is strict. Race reproducibility depends on scheduling. Signal handling is global and uses longjmp from the handler to keep the test alive.

## Test signals
The test passes if the entire stress loop completes without `SIGBUS`; any SIGBUS flips the final result to failure.
