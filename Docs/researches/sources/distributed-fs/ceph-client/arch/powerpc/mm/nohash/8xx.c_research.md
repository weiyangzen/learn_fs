# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/8xx.c

Purpose: initializes and later tightens 8xx nohash MMU mappings using large TLB/page-table entries for lowmem and IMMR.

Important APIs and control flow: `v_block_mapped()`/`p_block_mapped()` report IMMR and block-mapped RAM translations. `mmu_mapin_immr()` installs the IMMR fixmap once. `mmu_mapin_ram()` maps executable kernel text/init text/data using 16 KiB, 512 KiB, and 8 MiB chunks, adjusts memblock limits, and records `block_mapped_ram`. `mmu_mark_initmem_nx()` and `mmu_mark_rodata_ro()` remap ranges with stricter permissions and optionally pin TLBs. `setup_initial_memory_limit()` caps early memory to 32 MiB.

State and dependencies: state includes `block_mapped_ram` and `immr_is_mapped`. It depends on early page-table allocation, huge PTE encodings, strict RWX/debug-pagealloc/KFENCE decisions, memblock, fixmap constants, and TLB flushing/pinning. Risks include wrong permission boundary alignment, stale TLBs after remap, failure to map IMMR before users need it, and unsupported first-memblock bases. Test signals include 8xx boot, strict kernel RWX, debug_pagealloc/KFENCE configs, IMMR users, and rodata/initmem permission checks.
