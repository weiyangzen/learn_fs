# sources/distributed-fs/ceph-client/arch/sparc/mm/tsb.c

Purpose: manages SPARC64 Translation Storage Buffers: kernel/user TSB flushing, per-mm TSB allocation and growth, TSB register setup, slab cache creation, and context destruction.

Important APIs/functions: exports `flush_tsb_kernel_range()`, `flush_tsb_user()`, `flush_tsb_user_page()`, `pgtable_cache_init()`, `tsb_grow()`, `init_new_context()`, and `destroy_context()`. Important helpers include `tsb_hash()`, `tag_compare()`, `setup_tsb_params()`, `tsb_size_to_rss_limit()`, and `tsb_destroy_one()`.

Control flow: flush paths hash virtual addresses to TSB slots and invalidate matching tags, using scan mode for very large kernel ranges. User flushes hold `mm->context.lock`, choose base or huge TSB, convert virtual to physical base for Cheetah+/hypervisor, and invalidate one or multiple hugepage hash entries. `tsb_grow()` selects a power-of-two TSB size from RSS, allocates a physically contiguous slab object, invalidates tags, copies old TSB contents when growing, installs new register parameters, synchronizes remote CPUs, then frees the old TSB.

State and persistence: per-mm context stores TSB pointers, entry counts, register values, map virtual addresses/PTEs, RSS growth limits, hypervisor descriptors, ADI tag storage, and locks. All state is runtime-only.

Dependencies and integration points: depends on TSB assembly helpers (`tsb_flush`, `tsb_init`, `copy_tsb`), `mmu_context`, SPARC TLB type selection, hypervisor TSB descriptors, slab caches, NUMA allocation, SMP TSB sync, hugepage/THP counters, and ADI tag storage teardown.

Risks: TSB growth races with hardware miss handlers and remote CPUs, so the context lock and post-install sync are critical. High-order allocation failures intentionally disable future growth. Wrong page-size register encoding or physical-address conversion can break every user TLB miss.

Test signals: fork/exec under growing RSS, hugepage and THP faults, memory pressure during TSB growth, SMP address-space migration, hypervisor and non-hypervisor machines, kernel range invalidation, and ADI tag storage cleanup.
