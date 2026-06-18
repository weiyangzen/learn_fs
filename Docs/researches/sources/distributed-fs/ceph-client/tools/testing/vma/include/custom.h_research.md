<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h -->
# sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h

## Purpose

`custom.h` contains VMA test harness definitions that intentionally customize kernel behavior for userspace testing.

## Important APIs, Types, and Functions

It declares or defines `mmap_min_addr`, `dac_mmap_min_addr`, `TASK_SIZE`, and `pr_warn_once`. It defines a test `struct anon_vma` with `was_cloned` and `was_unlinked` flags. Inline helpers include `unlink_anon_vmas()`, `vma_start_write()`, `vma_start_write_killable()`, `anon_vma_clone()`, `__anon_vma_prepare()`, `anon_vma_prepare()`, `vma_lock_init()`, and `vma_kernel_pagesize()`.

## Control Flow and State

The helpers deliberately mutate test-visible fields rather than performing full kernel anon-vma locking and RMAP behavior. `vma_start_write*()` increments `vm_lock_seq` so tests can observe write locking. `anon_vma_prepare()` allocates a small anon-vma object with `calloc`.

## Dependencies and Integration Points

It depends on VMA harness definitions from `dup.h` and stubs, libc allocation, and kernel VMA code expecting anon-vma APIs. It integrates with tests that assert clone/unlink/write-lock side effects.

## Risks and Test Signals

Risks include over-simplifying anon-vma semantics, memory leaks in test-only allocations, and `TASK_SIZE` assumptions fixed to a 47-bit user address space. VMA unit tests checking cloned/unlinked markers and lock sequence changes validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/include/custom.h -->
