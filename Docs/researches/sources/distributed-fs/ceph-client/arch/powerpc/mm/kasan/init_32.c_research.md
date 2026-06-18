# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/init_32.c

Purpose: supplies common 32-bit PowerPC KASAN early, main, and late initialization helpers used by platform specializations.

Important APIs and control flow: `kasan_early_init()` maps the entire shadow through the early shadow page. `kasan_mmu_init()` prepopulates shadow page tables for hash MMU. `kasan_init()` maps real lowmem ranges using `kasan_init_region()`, optionally initializes KASAN vmalloc shadow page tables, remaps early shadow read-only, clears it, enables reports, and calls generic KASAN init. `kasan_late_init()` unmaps vmalloc/module early shadow for KASAN_VMALLOC. Helpers update early shadow PTEs and allocate replacement PTE pages through memblock.

State and dependencies: state includes `kasan_early_shadow_page`, early shadow PTEs, `init_mm` page tables, memblock allocations, and `init_task.kasan_depth`. Dependencies include MMU feature detection, TLB flushing, lowmem bounds, and platform weak `kasan_init_region()` overrides. Risks are writeable zero shadow remaining after init, vmalloc shadow overlap, missing lowmem ranges, and early boot recursion. Test signals include 32-bit KASAN boot across hash/nohash, vmalloc KASAN tests, and lowmem-only coverage checks.
