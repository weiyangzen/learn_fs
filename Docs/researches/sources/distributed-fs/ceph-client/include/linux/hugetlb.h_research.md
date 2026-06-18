# sources/distributed-fs/ceph-client/include/linux/hugetlb.h

## Purpose
Provides the central hugetlb and hugetlbfs interface: reservation maps, subpools, hstate accounting, hugepage page-table walking, page flags, allocation/freeing, migration, bootmem/CMA setup, and hugetlbfs inode/superblock helpers.

## APIs, Control Flow, and State
The main state types are `struct hugepage_subpool`, `struct resv_map`, `struct file_region`, `struct hugetlb_vma_lock`, `struct hstate`, and `struct huge_bootmem_page`. `hstate` persists pool counts and per-node free/surplus/max counts; reservation state persists in `resv_map` regions and cgroup uncharge metadata. Key APIs cover VMA duplication/reservation cleanup, table copy/move/unmap, `hugetlb_fault()`, `hugetlb_reserve_pages()`, `hugetlb_unreserve_pages()`, `huge_pte_alloc()`, `hugetlb_walk()`, PMD sharing/unsharing, vma locks, protection changes, page allocation, page-cache insertion, dissolution, migration support, and mm usage accounting. Control flow is lock-sensitive: shared mappings require hugetlb VMA locks or mapping `i_mmap_rwsem` for stable page-table walks; `huge_pte_lockptr()` selects lock level based on hugepage size.

## Dependencies, Integration, Risks, and Tests
Depends on MM, fs, page-table, userfaultfd, cgroup, mempolicy, architecture `asm/hugetlb.h`, CMA, NUMA, and memory-failure support. Integration spans hugetlbfs, shm, page fault, migration, memory hotplug, hwpoison, bootmem, sysfs/proc meminfo, and TLB flushing. Risks include reservation leaks, incorrect cgroup uncharges, unsafe PMD sharing walks, wrong page flag synchronization, gigantic page fallback breaking per-node pools, and disabled-config stubs that either BUG or silently return neutral values. Test signals include hugetlb selftests, meminfo/node counters, reservation/subpool accounting, PMD sharing stress, userfaultfd hugetlb tests, migration/hwpoison tests, and config-matrix builds.
