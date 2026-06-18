# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_madv_vs_map.c

## Purpose
`hugetlb_madv_vs_map.c` tests a race between `MADV_DONTNEED`, writes to an allocated hugetlb page, and a concurrent attempt to map an extra hugetlb page when only one hugepage should be available.

## Important APIs, types, and functions
`touch()` writes repeatedly to the primary hugepage. `madv()` repeatedly discards it with `MADV_DONTNEED`. `map_extra()` repeatedly attempts a second `MAP_HUGETLB` mapping and returns the pointer if allocation succeeds.

## Control flow
`main()` requires exactly one free hugepage and a default hugepage size. It loops ten times, mapping the single hugepage, launching the three racing threads, joining them, failing immediately if `map_extra()` succeeded, and unmapping before the next iteration.

## State and persistence behavior
The single hugepage oscillates between used and reserved/free-like states due to `MADV_DONTNEED`, while the test verifies another mapping cannot steal it. No durable state remains beyond the hugepage pool count.

## Dependencies and integration points
Requires pthreads, hugetlb, and a controlled system with exactly one free hugepage. Uses `vm_util.h` for free count and page size.

## Risks and edge cases
The race is scheduler dependent and intentionally sensitive to hugepage reservation accounting. If other processes use hugepages, the test either skips or becomes unreliable.

## Test signals
Success is returning `KSFT_PASS` after all iterations with no successful extra mapping; any unexpected extra hugepage mapping is a failure.
