<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c

## Purpose
`mm.c` manages nVHE hypervisor stage-1 mappings, private virtual address allocation, vmemmap backing, fixmap/fixblock temporary mappings, protected stacks, branch-prediction vectors, and host-provided memcache admission for pKVM.

## Important APIs, Types, and Functions
`pkvm_pgtable` and `pkvm_pgd_lock` hold the hyp stage-1 page table. `hyp_memory[]` and `hyp_memblock_nr` describe physical memory. `pkvm_alloc_private_va_range()` and `__pkvm_create_private_mapping()` reserve private VA space above `__io_map_base`. `pkvm_create_mappings()` maps linear hyp addresses. `hyp_back_vmemmap()` maps `struct hyp_page` backing memory. `pkvm_cpu_set_vector()` and `hyp_map_vectors()` select direct or spectre-hardened vectors. `hyp_fixmap_map()` / `hyp_fixmap_unmap()` and `hyp_fixblock_map()` / `hyp_fixblock_unmap()` provide temporary PA access. `hyp_create_idmap()`, `hyp_create_fixmap()`, `pkvm_create_stack()`, and `refill_memcache()` support setup and runtime allocation.

## Control Flow, State, and Persistence
`hyp_create_idmap()` establishes the initial idmap and computes the private VA layout for IO mappings and vmemmap. Private VA allocation monotonically advances `__io_map_base` and never frees ranges. Fixmap creation maps placeholder leaves, captures their PTE pointers, invalidates them, and later rewrites them by hand with required TLB invalidation. Protected stacks allocate a guard page plus mapped stack page(s), returning a top-of-stack address. `refill_memcache()` copies the host memcache, donates pages from host to hyp, and updates the host-visible memcache only after top-up.

## Dependencies and Integration Points
It integrates `setup.c` initialization, `mem_protect.c` ownership transitions, page-table primitives, hyp allocator mm ops, spectre vector selection, host SVE mappings, and trace/memory helpers that need temporary physical mappings.

## Risks and Test Signals
Risks include private VA exhaustion, fixmap break-before-make violations, incorrect TLB invalidation when rewriting PTEs, guard-stack alignment assumptions, vmemmap overlap with IO space, and memcache donation races. Test signals are pKVM initialization, vmemmap-backed allocator use, stack overflow detection, fixmap/fixblock stress on PAGE_SHIFT variants, spectre vector selection, and memcache refills with partial host page lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/mm.c -->
