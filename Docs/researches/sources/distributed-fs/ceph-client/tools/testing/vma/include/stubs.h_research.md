<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h

## Purpose

`stubs.h` supplies no-op or simplified kernel APIs for the userspace VMA harness. It lets imported mm/VMA code compile without pulling in page tables, mempolicy, userfaultfd internals, KSM, locking, and filesystem internals.

## Important APIs, Types, and Functions

It forward-declares many kernel structs, defines attributes and constants, and stubs functions such as `userfaultfd_unmap_complete()`, `move_page_tables()`, `free_pgd_range()`, `ksm_execve()`, `ksm_exit()`, `vma_numab_state_init/free()`, anon-vma-name helpers, mmap action hooks, `fixup_hugetlb_reservations()`, `shmem_file()`, `ksm_vma_flags()`, PFN remap hooks, `do_munmap()`, lock helpers, `userfaultfd_unmap_prep()`, `can_modify_mm()`, `arch_unmap()`, `mpol_equal()`, `khugepaged_enter_vma()`, and VMA property predicates.

## Control Flow and State

Most functions either return success, return false, return input flags, or do nothing. They intentionally remove side effects outside the VMA algorithms under test.

## Dependencies and Integration Points

It is included by the VMA harness before imported kernel mm code. It depends on basic types from `dup.h` and shared kernel compatibility headers.

## Risks and Test Signals

Risks include masking failures in page-table moves, unmap completion, mempolicy, KSM, userfaultfd, locking, and filesystem interactions. The test harness should use these stubs only for VMA logic whose correctness can be asserted without those subsystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/stubs.h -->
