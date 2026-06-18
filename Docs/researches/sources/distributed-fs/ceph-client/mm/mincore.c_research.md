# sources/distributed-fs/ceph-client/mm/mincore.c

## Purpose
Implements the `mincore(2)` system call, which reports whether pages in the calling process's virtual address range are resident enough that a fault would not need I/O. It walks VMAs and page tables, checks page cache and swap cache state for unmapped file-backed ranges, handles hugetlb and transparent huge mappings, and applies the kernel's side-channel mitigation for page-cache residency visibility.

## Important APIs, Types, and Functions
The user-visible entry point is `SYSCALL_DEFINE3(mincore)`. Important helpers are `do_mincore()`, `mincore_pte_range()`, `mincore_unmapped_range()`, `__mincore_unmapped_range()`, `mincore_page()`, `mincore_swap()`, `mincore_hugetlb()`, and `can_do_mincore()`. The page walker is configured by `mincore_walk_ops` with PMD, PTE-hole, hugetlb, and read-lock behavior.

## Control Flow
The syscall untags and validates the start address, requires page alignment, checks the user range and result vector with `access_ok()`, allocates one temporary page of bytes, and processes at most `PAGE_SIZE` residency entries per loop. For each chunk it takes `mmap_read_lock()`, calls `do_mincore()`, releases the lock, and copies the bytes to userspace.

`do_mincore()` finds the VMA covering the current address and limits the chunk to the VMA end. If the VMA is not eligible for precise residency visibility, it fills the result with `1`s to avoid leaking file page-cache state. Otherwise `walk_page_range()` drives `mincore_pte_range()`, `mincore_unmapped_range()`, and `mincore_hugetlb()`. Present PTEs and PMD-mapped THPs report resident, swap entries are checked through `mincore_swap()`, and PTE holes or markers in file-backed mappings consult `mincore_page()` to query the page cache.

## State and Persistence Behavior
The syscall does not persist kernel state. It briefly allocates a temporary kernel page, walks page tables under the mmap read lock and page-table locks, may take swap device references for shmem swap lookups, and gets transient folio references from filemap or swapcache lookups. Results are intentionally a snapshot; residency can change immediately after locks are dropped.

## Dependencies and Integration Points
The implementation depends on pagewalk, pgtable helpers, hugetlb, swapcache, shmem, filemap XArray entries, VMA lookup, and usercopy helpers. The visibility policy integrates with inode ownership/capability checks and `file_permission(..., MAY_WRITE)` to avoid exposing page-cache residency for files the caller could not write.

## Risks and Edge Cases
Important edge cases include partially covered VMAs, invalid gaps returning `-ENOMEM`, huge pages whose subpages must all receive the same byte, shmem swapin error entries, migration/hwpoison markers, swap disabled builds, concurrent page-table changes that require `ACTION_AGAIN`, and user vector faults. The side-channel behavior is subtle: denied non-anonymous mappings are reported as resident rather than failing or revealing actual cache state.

## Test Signals
Tests should cover anonymous resident and nonresident pages, file-backed cached and uncached pages with allowed and denied permissions, tmpfs/shmem swapped pages, hugetlb mappings, THP mappings, holes across VMA boundaries, unaligned start returning `-EINVAL`, invalid address ranges returning `-ENOMEM`, bad result vectors returning `-EFAULT`, and repeated calls under concurrent reclaim/migration to validate snapshot rather than stability semantics.
