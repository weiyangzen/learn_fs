# sources/distributed-fs/ceph-client/arch/parisc/mm/init.c

Purpose: initializes PA-RISC memory management, including physical memory ranges, memblock reservations, kernel page tables, gateway and fixmap mappings, BTLB entries, space-ID allocation, TLB flushing, protection maps, and execmem setup.

Important APIs and state: exports `swapper_pg_dir`, initial PTE/PMD arrays, `pmem_ranges`, `parisc_vmalloc_start`, `paging_init()`, `mem_init()`, `free_initmem()`, `set_kernel_text_rw()`, `mark_rodata_ro()`, `alloc_sid()`, `free_sid()`, `flush_tlb_all()`, `btlb_init_per_cpu()`, and optional `execmem_arch_setup()`. Static state tracks system RAM resources, `mem_limit`, kernel read-only transition, BTLB data, and space-ID bitmaps.

Control flow: boot starts with `setup_bootmem()`, which sorts firmware memory ranges, applies gaps and `mem=`, registers resources, reserves firmware/kernel/initrd/hole memory, initializes PDT, and configures memblock. `pagetable_init()` maps all physical ranges; `gateway_init()` maps the gateway page; `fixmap_init()` allocates fixmap page tables; `paging_init()` flushes caches/TLBs. Later functions harden kernel mappings, free init memory, set vmalloc layout, and manage TLB space IDs.

State and persistence: this file establishes persistent kernel mappings and memory resources. Space IDs are allocated under `sid_lock`, freed into dirty bitmaps, and recycled only after global TLB flush.

Dependencies and integration: consumes firmware inventory, memblock, generic MM, cache/TLB code, pdc/chassis/PDT helpers, fixmap headers, and mmu context code.

Risks: early mapping size limits require bottom-up memblock allocation. Incorrect memory range truncation or hole reservation can corrupt memory. Space-ID recycling before TLB purge would create address-space aliasing. RWX-to-RO transitions must be synchronized with cache and TLB flushing.

Test signals: boot on 32-bit and 64-bit PA-RISC, sparsemem and non-sparsemem, `mem=` limits, initrd above limit, strict RWX, SMP TLB flush recycling, BTLB insertion, vmalloc start on PCXL, and execmem users.
