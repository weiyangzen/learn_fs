# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/split_huge_page_test.c

Purpose: validates debugfs-triggered splitting of PMD THPs, PTE-mapped THPs, file-backed THPs, and large pagecache folios into requested lower orders without data corruption.

Important APIs and functions: `write_debugfs()` writes requests to `/sys/kernel/debug/split_huge_pages`; `is_backed_by_folio()`, `gather_after_split_folio_orders()`, and `check_after_split_folio_orders()` inspect pagemap/kpageflags; split routines cover zero-filled anonymous THPs, target orders, remapped PTE THPs, tmpfs THPs, and pagecache THPs with optional in-folio offset.

Control flow: `main()` requires root and THP, initializes page/PMD sizes and expected-order arrays, opens pagemap/kpageflags, runs all split cases, optionally uses supplied XFS path or a temporary directory, then cleans resources.

State and dependencies: uses debugfs, temporary tmpfs mounts, optional XFS path, files under `/tmp`, `drop_caches`, and global fds. Depends on root, THP, pagemap PFN visibility, kpageflags, and filesystem large-folio support.

Risks and test signals: strong signals are preserved byte patterns, expected folio-order histograms, absence of huge mappings, and RSS decrease for zero-filled splits. Failure exits may leave temp mounts/files.
