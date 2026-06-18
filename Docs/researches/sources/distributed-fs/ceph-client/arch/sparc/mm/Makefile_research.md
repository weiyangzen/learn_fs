# sources/distributed-fs/ceph-client/arch/sparc/mm/Makefile

Purpose: Kbuild manifest for SPARC-specific memory-management objects.

Important APIs/functions: selects `fault_$(BITS).o` and `init_$(BITS).o` for all builds. Adds SPARC64 `ultra.o`, `tlb.o`, `tsb.o`; SPARC32 SRMMU/IOMMU/cache CPU support objects; `hugetlbpage.o` when huge pages are enabled; and `execmem.o` when executable memory allocation is configured.

Control flow: object inclusion is controlled by `CONFIG_SPARC64`, `CONFIG_SPARC32`, `CONFIG_HUGETLB_PAGE`, and `CONFIG_EXECMEM`.

State and persistence: build-time only.

Dependencies/integration: coordinates architecture MM initialization, fault handling, TLB/TSB management, platform-specific cache/TLB ops, and DMA/IOMMU support.

Risks: incorrect config gating can link incompatible 32/64-bit objects or omit platform cache/TLB operations. New MM features must be added under the correct architecture config.

Test signals: build matrix for SPARC32, SPARC64, hugepage enabled/disabled, execmem enabled/disabled, and SBUS/SRMMU platform configs.
