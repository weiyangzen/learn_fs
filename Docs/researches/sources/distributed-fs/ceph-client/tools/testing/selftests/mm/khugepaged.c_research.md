# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/khugepaged.c

## Purpose
`khugepaged.c` is a comprehensive Transparent Huge Page collapse test harness. It compares background `khugepaged` collapse and explicit `MADV_COLLAPSE` across anonymous, file-backed, and shmem mappings, validating collapse eligibility, scan limits, swap/shared constraints, compound-page handling, fork behavior, and file page-cache interactions.

## Important APIs, types, and functions
The core abstraction is `struct mem_ops`, with setup/cleanup/fault/check implementations for anon, file, and shmem. `struct collapse_context` abstracts the collapse engine, either `khugepaged_collapse()` or `madvise_collapse()`. The file also tracks `struct file_info` for file/shmem backing and block-device readahead sysfs path. Helpers include THP settings save/restore via `thp_settings.h`, `get_finfo()`, `check_swap()`, `alloc_mapping()`, `fill_memory()`, `validate_memory()`, `madvise_collapse_retry()`, `alloc_hpage()`, and many `collapse_*` scenarios.

## Control flow
`main()` verifies THP availability, parses `<context>:<mem_type>` and optional anon mTHP order, computes page and PMD hugepage sizes, configures THP/khugepaged settings, and runs a matrix of scenario functions through selected contexts and memory types. Setup functions create fixed-address mappings at `BASE_ADDR`: anonymous mappings, read-only file mappings with page cache drop and disabled readahead, or shared memfd shmem mappings. Collapse functions either mark ranges `MADV_HUGEPAGE` and wait for khugepaged scans or temporarily disable THP and issue `MADV_COLLAPSE` directly.

## State and persistence behavior
The harness deliberately changes global THP and khugepaged sysfs settings, device queue readahead, `/proc/sys/vm/drop_caches`, temporary files, memfds, swap state, and mappings. It saves settings at start and restores them through `atexit()` and signal handlers. Test data uses a deterministic `0xdead0000 + page index` pattern to detect corruption after collapse, split, fork, swap, and remap operations.

## Dependencies and integration points
The file depends on `vm_util.h` and `thp_settings.h`, `/sys/kernel/mm/transparent_hugepage`, `/proc/self/smaps`, `/proc/sys/vm/drop_caches`, file THP support for read-only filesystem collapse, tmpfs `huge=advise` for shmem khugepaged cases, and optional swap for swap tests. File-backed tests require a directory argument and inspect block device sysfs.

## Risks and edge cases
The test runs at a fixed virtual address and can fail if unavailable. It mutates system-wide THP settings and page cache. Khugepaged tests rely on scan timing; `wait_for_scan()` uses a timeout based on `full_scans`. MADV_COLLAPSE can transiently return `EAGAIN`, so the helper retries once. Some scenarios skip tmpfs or non-applicable memory types where semantics differ.

## Test signals
Output is color-coded success/fail/skip and `exit_status` accumulates failures. Passing means collapse succeeds or fails exactly as expected, `check_huge_*()` observes the right PMD mapping count, and `validate_memory()` finds no corruption after every scenario.
