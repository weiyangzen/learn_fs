# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/mmu_context.c

Purpose: Allocates, initializes, switches, and destroys Book3S64 MMU contexts for both hash and radix translation modes.

Important APIs and functions: Context ID management uses `alloc_context_id()`, `hash__reserve_context_id()`, `hash__alloc_context_id()`, `__destroy_context()`, and `destroy_contexts()`. Lifecycle APIs include `init_new_context()`, `destroy_context()`, `arch_exit_mmap()`, and `cleanup_cpu_mmu_context()`. Hash helpers include `hash__init_new_context()` and `hash__setup_new_exec()`. Radix helpers include `radix__init_new_context()` and `radix__switch_mmu_context()`.

Control flow: Hash initialization allocates `hash_mm_context`, initializes or copies slice/subpage state depending on exec versus fork, reallocates all required context IDs, and initializes pkeys. Radix initialization allocates a PID from `mmu_base_pid`, writes the process table entry with the mm PGD and RTS field, issues `ptesync;isync`, and clears hash context. `init_new_context()` selects radix or hash, stores `mm->context.id`, initializes page-table fragment caches, IOMMU list, active CPU count, and copro count. Destruction clears radix process table entries when needed, frees hash subpage state or process IDs, frees hash context, and marks `MMU_NO_CONTEXT`. `arch_exit_mmap()` destroys fragment caches and clears radix process table before fullmm TLB flush.

State and persistence: Global state is the `IDA` context allocator. Per-mm persistent state includes context ID(s), hash context pointer, pte/pmd fragment caches, IOMMU registration list, active CPU/copro counters, and radix process table entries.

Dependencies and integration: Integrates with slice management, pkeys, pte/pmd fragment allocators, SPAPR TCE IOMMU, radix process tables, CPU hotplug, and generic task/mm lifecycle hooks.

Risks: Error unwinding during hash extended ID reallocation must not free inherited IDs incorrectly. Radix process table stores must be ordered before PID use. Fragment cache destruction must account for partial page-table pages. Teardown ordering with fullmm flush avoids stale process table caches.

Test signals: Fork/exec/exit loops under hash and radix, context ID exhaustion, subpage protection inheritance, pkeys initialization, mm teardown with IOMMU preregistration, CPU hotplug TLB flush, and radix PID switch tests are relevant.
