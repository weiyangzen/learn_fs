# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-madvise.c

## Purpose
`hugetlb-madvise.c` tests `MADV_DONTNEED` and `MADV_REMOVE` on anonymous and file-backed hugetlb mappings, with attention to alignment, invalid ranges, private versus shared mappings, and hugepage free-count accounting.

## Important APIs, types, and functions
The test uses `default_huge_page_size()`, `get_free_hugepages()`, `memfd_create(MFD_HUGETLB)`, `mmap(MAP_HUGETLB)`, `fallocate()`, `madvise()`, and `munmap()`. `validate_free_pages()` asserts exact free hugepage counts. `write_fault_pages()` and `read_fault_pages()` force allocation or read faults.

## Control flow
`main()` skips when fewer than 20 free hugepages are available, creates a hugetlb memfd, then runs a sequence: invalid start/end `MADV_DONTNEED` ranges, unaligned start and length alignment behavior, anonymous private `MADV_DONTNEED`, private file mapping behavior before and after CoW, shared file mapping behavior, `MADV_REMOVE` on shared mappings, and combined shared/private mappings of the same file.

## State and persistence behavior
The test allocates and frees hugetlb pages and uses exact free-page counts as the observable state. `MADV_DONTNEED` should free anonymous/private CoW hugepages but not file-backed reserved pages; `MADV_REMOVE` acts like hole punch and frees file pages. Comments document expected historical behavior where hole punching shared file pages also frees private mapping pages.

## Dependencies and integration points
Requires a configured hugetlb pool and kernel hugetlb memfd support. It depends on `vm_util.h` hugepage accounting helpers and kselftest skip codes.

## Risks and edge cases
Exact free-page assertions are fragile if other system activity consumes hugepages concurrently. Filesystem or kernel changes to historical private-page behavior would change expected counts. The test exits on first failed assertion using `exit(1)`.

## Test signals
Passing means every page-count transition matches the expected allocation/free model and invalid/unaligned `madvise()` calls fail or round as expected.
