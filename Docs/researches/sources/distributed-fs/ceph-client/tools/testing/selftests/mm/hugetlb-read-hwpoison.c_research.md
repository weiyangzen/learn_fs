# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/hugetlb-read-hwpoison.c

## Purpose
`hugetlb-read-hwpoison.c` is a HugeTLB read regression test that verifies ordinary reads and reads around `MADV_HWPOISON`ed subpages of a hugepage. It checks both sequential reads from the start and seeked reads that skip poisoned areas.

## Important APIs, types, and functions
The program defines `enum test_status`, status formatting, chunk pattern helpers `setup_filemap()` and `verify_chunk()`, read helpers `read_hugepage_filemap()` and `seek_read_hugepage_filemap()`, test bodies `test_hugetlb_read()` and `test_hugetlb_read_hwpoison()`, and `create_hugetlbfs_file()` using `memfd_create(MFD_HUGETLB)` plus `fstatfs(HUGETLBFS_MAGIC)`.

## Control flow
`main()` iterates write/read chunk sizes from half a base page through four base pages. For each chunk size it creates a fresh hugetlb memfd, runs the plain read regression, creates another file for a read that should stop after reaching a poisoned page, and creates another for a seeked read that starts past the poisoned subpage. Each test truncates, maps with `MAP_SHARED | MAP_POPULATE`, writes chunk patterns, optionally poisons a base page inside the hugepage, reads, validates content and byte counts, unmaps, truncates back to zero, and closes.

## State and persistence behavior
The test uses temporary hugetlb memfds, populates their page cache, injects hardware-poison state via `MADV_HWPOISON`, and then truncates files back to zero. Poisoning can have system-level side effects on the hugepage pool, so the test assumes a controlled selftest environment.

## Dependencies and integration points
Requires hugetlb memfd support, `MADV_HWPOISON` permission/configuration, and enough hugepages. It relies on standard `read()` behavior for hugetlbfs files around poisoned base pages.

## Risks and edge cases
`MADV_HWPOISON` can require privileges and may be disabled. Pattern validation is sensitive to chunk-size arithmetic. The test returns failure immediately on any `TEST_FAILED` result but treats mapping/setup failures as skipped until final create failure.

## Test signals
Pass conditions are exact total bytes read and byte pattern verification for plain, poisoned, and seek-past-poison read modes across all chunk sizes.
