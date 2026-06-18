# sources/distributed-fs/ceph-client/mm/mseal.c

Purpose: implements the `mseal` syscall, which marks a fully mapped virtual address range as sealed so later metadata-changing operations such as `munmap`, `mremap`, MAP_FIXED replacement, `mprotect`, pkey changes, and selected destructive advice can be denied by other MM paths.

Important APIs/types/functions: `do_mseal`, syscall `mseal`, `range_contains_unmapped`, and `mseal_apply`. Key types are `mm_struct`, `vm_area_struct`, `vma_iterator`, and `vma_flags_t`; the important state bit is `VMA_SEALED_BIT`.

Control flow: `do_mseal` rejects nonzero flags, strips address tags, requires a page-aligned start, page-aligns length, rejects length wrap and range overflow, and treats zero-length ranges as success. It then takes `mmap_write_lock_killable`, scans the range with `range_contains_unmapped` to ensure the start, middle, and end contain no holes, and on success makes a second pass with `mseal_apply`. The apply pass splits/merges VMAs as needed through `vma_modify_flags`, starts VMA write synchronization, and sets `VMA_SEALED_BIT`; already sealed VMAs are skipped as a no-op.

State and persistence: sealing is persistent in the process address space as a VMA flag until the VMA is destroyed with the process. There is no unseal operation. No disk data is written. The range must be completely mapped at seal time because unmapped holes could later be filled with unsealed mappings and mislead callers about the protected extent.

Dependencies and integration points: uses mmap write locking, VMA iterators, VMA flag modification helpers, and `internal.h`. Other files enforce the seal: `mprotect_fixup` returns `-EPERM`, `mremap` rejects sealed VMAs, and unmap/MAP_FIXED/madvise paths are expected to consult VMA sealing before destructive metadata changes.

Risks: the two-pass scan/apply logic relies on the write lock to keep topology stable. Range-hole detection must catch leading, internal, and trailing gaps. VMA splitting/merging can still fail with OOM or map-count pressure. Any MM path that modifies sealed metadata but forgets to check `vma_is_sealed` would undermine the syscall guarantee.

Test signals: `mseal` syscall tests for alignment, flags, zero length, overflow, unmapped leading/internal/trailing holes, repeated sealing, partial-VMA sealing that forces splits, and denial of `mprotect`, `pkey_mprotect`, `mremap`, `munmap`, and MAP_FIXED replacement after sealing. Stress tests should include map-count/OOM split failures and concurrent faults while sealing under the write lock.
