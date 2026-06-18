# sources/distributed-fs/ceph-client/arch/mips/mm/highmem.c

Purpose: minimal MIPS highmem support globals and kmap TLB flush hook.

Important APIs/functions: defines `highstart_pfn` and `highend_pfn`. `kmap_flush_tlb(unsigned long addr)` calls `flush_tlb_one(addr)` and is exported.

Control flow: no complex flow; this file supplies architecture glue used by generic highmem/kmap code.

State and persistence: highmem PFN bounds are global boot/runtime state set by memory initialization elsewhere.

Dependencies and integration: depends on fixmap and TLB flush helpers. Built only under `CONFIG_HIGHMEM`.

Risks and test signals: highmem is incompatible with dcache aliasing in `init.c`, so test highmem boot only on supported CPUs. Validate kmap/kunmap TLB invalidation under local and SMP workloads.
