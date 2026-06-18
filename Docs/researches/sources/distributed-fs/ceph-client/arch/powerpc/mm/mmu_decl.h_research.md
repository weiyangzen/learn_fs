# sources/distributed-fs/ceph-client/arch/powerpc/mm/mmu_decl.h

Purpose: declares internal PowerPC MMU functions and shared globals used across architecture MM source files.

Important APIs and control flow: it exposes nohash local/global TLB invalidation helpers, 32-bit mapping initialization hooks, e500 CAM/KASLR routines, block-mapping lookup APIs, strict RWX marking hooks, 8xx IMMR mapping, debug-pagealloc/KFENCE helper, hotplug section mapping, and hash kernel page toggling. Several functions become inline no-ops when their architecture family is not enabled.

State and dependencies: declared state includes memory sizing globals, e500 `TLBCAM[]`, and architecture routines implemented in nohash/hash files. It depends heavily on Kconfig to select correct inline versus extern definitions and includes trace support for nohash TLB operations. Risks are ABI drift between declarations and implementations, incorrect no-op selection hiding missing functionality, and trace/invalidation prototype mismatches. Test signals are allmodconfig-style builds across PowerPC MMU families, sparse/prototype checks, and link coverage for hotplug, KASLR, e500, 8xx, and Book3S variants.
