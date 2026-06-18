# sources/distributed-fs/ceph-client/arch/x86/mm/init.c

## Purpose
Initializes core x86 memory-management state: PAT cache-mode translation tables, early page-table allocation, direct physical mappings, CR4 paging features, PCID gating, memory-map strategy, text-poke address space, `/dev/mem` restrictions, freeing init memory, zone limits, TLB state, swap limits, and executable-memory ranges.

## Important APIs, Types, And Functions
Key functions include `cachemode2protval()`, `pgprot2cachemode()`, `x86_has_pat_wp()`, `alloc_low_pages()`, `early_alloc_pgt_buf()`, `init_memory_mapping()`, `init_mem_mapping()`, `poking_init()`, `devmem_is_allowed()`, `free_init_pages()`, `free_kernel_image_pages()`, `free_initmem()`, `arch_zone_limits_init()`, `update_cache_mode_entry()`, `arch_max_swapfile_size()`, and `execmem_arch_setup()`.

## Control Flow
Boot initializes early page-table buffers, probes large-page/PGE/GB-page support, disables or enables PCID based on CPU/microcode constraints, maps ISA memory, initializes the trampoline, maps RAM ranges top-down or bottom-up using memblock and E820 RAM ranges, loads `swapper_pg_dir`, flushes TLBs, invokes hypervisor hooks, and runs early memtest. Helper paths split ranges by large-page alignment, allocate low page tables from BRK/memblock/free pages, track mapped PFN ranges, and later free init/initrd memory with NX/RW or not-present protections.

## State And Persistence
Mutates global PAT translation tables, PFN mapped ranges, `max_pfn_mapped`, `max_low_pfn_mapped`, `min_pfn_mapped`, CR4 feature masks, page tables, memblock allocations, TLB state, `text_poke_mm`, and executable memory policy. Many variables are `__initdata`, while PAT/TLB/execmem state persists.

## Dependencies And Integration Points
Integrates with E820, memblock, PAT, MTRR/cache attributes, PTI, KASLR, hypervisors, text patching, TLB flushing, debug pagealloc, kmemleak, memory encryption cleanup, `/dev/mem`, L1TF mitigation, module/kprobe/ftrace/BPF executable allocators, and architecture page-table constructors.

## Risks
Boot-time ordering is critical: page tables must be allocated from mapped memory and direct mappings must avoid holes that MTRRs cannot mark UC. Large-page selection affects performance and correctness with debug pagealloc and memory holes. PCID is disabled for specific microcode errata. Freeing init memory must avoid leaving freed secrets mapped in PTI user-visible aliases. `/dev/mem` policy must not expose system RAM.

## Test Signals
Boot across 32/64-bit, 4/5-level paging, KASLR, PTI, PSE/PGE/GB pages, PCID microcode errata, top-down and bottom-up memblock, sparse E820 holes, Xen/hypervisor hooks, debug pagealloc, strict devmem, initrd freeing, L1TF swap-size limiting, and execmem allocation for modules/kprobes/ftrace/BPF.
