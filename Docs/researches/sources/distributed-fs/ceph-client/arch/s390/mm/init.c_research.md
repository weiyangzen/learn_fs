## sources/distributed-fs/ceph-client/arch/s390/mm/init.c

Purpose: initializes core s390 memory-management state: kernel page directories, zero pages, zone limits, vmem mapping, protected virtualization DMA sharing, per-cpu areas, memory hotplug, CMA offline restrictions, and executable-memory ranges.

Important APIs, types, and functions: global exported state includes `swapper_pg_dir`, `invalid_pg_dir`, `s390_invalid_asce`, noexec masks, `empty_zero_page`, `zero_page_mask`, and `__per_cpu_offset`. Functions include `arch_setup_zero_pages()`, `arch_zone_limits_init()`, `paging_init()`, `mark_rodata_ro()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `force_dma_unencrypted()`, `arch_mm_preinit()`, `memory_block_size_bytes()`, `setup_per_cpu_areas()`, memory hotplug `arch_add_memory()`/`arch_remove_memory()`, and `execmem_arch_setup()`.

Control flow: early setup allocates a power-of-two zero-page pool sized by available memory and sets `zero_page_mask`. `paging_init()` initializes virtual memory mappings and the 31-bit DMA zone limit. `mark_rodata_ro()` enables instruction-execution protection when NX exists and write-protects ro-after-init data. Protected virtualization setup registers restricted virtio memory access and forces SWIOTLB shared bounce buffers. Per-cpu setup uses `pcpu_embed_first_chunk()` and fills offsets. Hot-add creates a vmem direct mapping before `__add_pages()` and unwinds on failure; hot-remove removes pages then tears down mapping. Execmem setup randomizes module load start under KASLR.

State and persistence: establishes long-lived global page directories, zero-page pool, noexec masks, per-cpu offset table, SWIOTLB/PV memory attributes, memory notifier for CMA, and execmem range metadata.

Dependencies and integration points: depends on memblock, vmem, pageattr, UV protected virtualization, SWIOTLB, virtio restricted memory access, CMA, memory hotplug, SCLP memory increment size, percpu allocator, KASLR, KASAN-aware execmem, and generic DMA APIs.

Risks: zero-page order must balance mapping granularity and small-memory pressure. PV encrypted/decrypted naming maps to UV shared/unshared state and is easy to misuse. Memory hotplug requires PAGE_KERNEL mappings and correct vmem unwind. CMA notifier prevents offlining memory that intersects CMA; missing this risks DMA allocation corruption.

Test signals: boot on normal and protected-virtualization guests, memory hot-add/remove, CMA offline rejection, `/proc/meminfo` direct-map counts via pageattr, per-cpu area sanity, rodata write-protection faults, and module allocation within `MODULES_VADDR` to `MODULES_END`.
