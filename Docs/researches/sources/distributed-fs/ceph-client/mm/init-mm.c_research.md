## sources/distributed-fs/ceph-client/mm/init-mm.c

Purpose: defines the kernel's singleton `init_mm` and a dummy VMA operations table used when a VMA's real hooks must no longer be invoked after failure or close handling.

Important APIs and data: exports `const struct vm_operations_struct vma_dummy_vm_ops`, initializes `struct mm_struct init_mm`, and provides `setup_initial_init_mm()` to fill kernel text/data/brk boundaries.

Control flow: initialization is static. `init_mm` starts with `swapper_pg_dir`, preinitialized maple tree state, reference counts, locks, optional per-VMA lock state, user namespace, scheduler MM CID lock, flexible-array initialization, and architecture-specific `INIT_MM_CONTEXT`. Later early boot calls `setup_initial_init_mm()` with linker-derived addresses.

State and persistence: `init_mm` is persistent global kernel state for kernel page tables and kernel mappings. It is not tied to a process lifetime and uses an NR_CPUS-sized cpumask strategy indirectly through static struct layout rather than dynamic allocation.

Dependencies and integration: integrates with architecture page tables, maple tree VMA storage, mmap locking, user namespaces, IOMMU/MMU context hooks, and many MM users that operate on kernel mappings.

Risks and test signals: incorrect static initialization can break kernel page-table walking, VMA accounting, locking, or architecture MM context assumptions. Test signals are mostly boot-time: successful boot, page table manipulation against `init_mm`, VMA fault/error paths that install `vma_dummy_vm_ops`, and lockdep coverage around initialized locks.
