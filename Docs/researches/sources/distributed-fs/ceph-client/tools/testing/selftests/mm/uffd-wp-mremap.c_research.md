<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c

## Purpose
Kselftest validating that UFFD write-protect markers are cleared after `mremap()` when `UFFD_FEATURE_EVENT_REMAP` is not enabled. It exercises base pages, transparent huge pages, swapped pages, shared/private mappings, and hugetlb pages across detected supported sizes.

## Important APIs, Types, and Functions
- `detect_thp_sizes()` reads THP supported orders and computes supported THP sizes.
- `mmap_aligned()` creates manually aligned mappings for large folio sizes.
- `alloc_one_folio()` allocates and populates a base page, THP, or hugetlb folio.
- `check_uffd_wp_state()` reads `/proc/self/pagemap` and validates the `PM_UFFD_WP` bit on each base page.
- `range_is_swapped()` validates successful `MADV_PAGEOUT`.
- `test_one_folio()` is the core scenario runner for one size/private/swapout/hugetlb combination.

## Control Flow
`main()` detects base page size, THP sizes, and hugetlb sizes, disables THP globally for the test when needed, sets the kselftest plan to the number of size/testcase combinations, opens pagemap, and calls `test_one_folio()` for each case. Each case allocates a folio, registers it for UFFD-WP, applies write protection, optionally pages it out, confirms WP bits are set, moves the mapping to a new aligned address with `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)`, and confirms WP bits are cleared.

## State and Persistence Behavior
State includes global page-size arrays, pagemap fd, and temporary THP settings via `thp_settings.h`. THP settings are saved, pushed, and restored. Mappings are unmapped and UFFD fds closed per case. Swapout state is transient kernel VM state.

## Dependencies and Integration Points
Uses `uffd-common.h`, `vm_util.h`, `thp_settings.h`, Linux UFFD and mmap ABI, `/proc/self/pagemap`, THP sysfs, hugetlb size detection, and kselftest plan/result APIs.

## Risks and Edge Cases
Cases can skip when userfaultfd is unavailable, THP or hugetlb allocation fails, swap is unavailable, or `MADV_PAGEOUT` does not actually swap the range. The aligned mapping logic assumes power-of-two folio sizes. Hugetlb swapout is explicitly disallowed by assertion.

## Test Signals
Each `test_one_folio(...)` emits a kselftest pass, fail, or skip line. Final exit is `ksft_exit_pass()` unless any failures are counted, in which case it reports the number failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-wp-mremap.c -->
