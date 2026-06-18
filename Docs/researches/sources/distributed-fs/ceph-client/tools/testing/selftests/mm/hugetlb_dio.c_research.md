# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb_dio.c

## Purpose
`hugetlb_dio.c` checks for hugepage leaks after direct I/O writes that use a hugetlb page as the user buffer. It verifies that the DIO path unpins the hugetlb buffer after aligned and selected unaligned offset/length cases.

## Important APIs, types, and functions
`get_dio_alignment()` uses `statx(AT_EMPTY_PATH, STATX_DIOALIGN)` to discover direct-I/O alignment. `check_dio_alignment()` skips cases that would fail before exercising the kernel pin/unpin path. `run_dio_using_hugetlb()` allocates one hugetlb page, writes a selected slice to an `O_DIRECT` tmpfile, unmaps the hugepage, and compares free hugepage counts before and after.

## Control flow
`main()` skips without free hugepages, opens an anonymous tmpfile in `/tmp` with `O_DIRECT`, discovers DIO alignment, sets a four-test plan, and runs cases with page-aligned start/end, aligned start with unaligned end, unaligned start with aligned end, and both unaligned. Cases incompatible with DIO alignment are reported skipped.

## State and persistence behavior
The test temporarily consumes one hugepage per case and writes data to an unnamed temporary file. The observed persistent state is the free hugepage count, which should return to the pre-allocation value after `munmap()`.

## Dependencies and integration points
Requires hugetlb availability, a filesystem under `/tmp` supporting `O_TMPFILE` and `O_DIRECT`, `statx` DIO alignment reporting, and `vm_util.h` hugepage counters.

## Risks and edge cases
Direct-I/O alignment constraints can skip unaligned cases. Concurrent hugepage users can make free-count comparison noisy. Filesystems without `O_DIRECT` tmpfile support skip the whole test.

## Test signals
Each executed case passes when `free_hugepages_after_munmap == free_hugepages_before_allocation`, indicating no lingering DIO pin.
