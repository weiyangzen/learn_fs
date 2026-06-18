# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/Makefile

Purpose: builds the nohash PowerPC MMU implementation objects selected by platform Kconfig.

Important APIs and control flow: common nohash objects are `mmu_context.o`, `tlb.o`, `tlb_low.o`, and `kup.o`. Book3E64 adds 64-bit TLB and page-table code, 44x/8xx/e500 add their platform MMU initializers, randomization adds `kaslr_booke.o`, and e500 HugeTLB adds the preload helper. KCOV is disabled for sensitive TLB and e500 code paths needed during early boot and exception handling.

State and dependencies: no runtime state, but object inclusion controls which declarations in `mmu_decl.h` resolve. Risks include missing platform files for configured MMU families, instrumenting code that runs before coverage runtime is safe, and incomplete HugeTLB support if e500 object selection changes. Test signals are Kconfig matrix builds for Book3E64, 44x, 8xx, e500, RANDOMIZE_BASE, HUGETLB_PAGE, and KCOV-enabled kernels.
