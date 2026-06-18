<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h

Purpose: Controls whether huge vmalloc mappings are supported on PowerPC.

Important APIs/types/functions: `arch_vmap_pud_supported()` and `arch_vmap_pmd_supported()` when `CONFIG_HAVE_ARCH_HUGE_VMAP` is enabled.

Control flow: vmalloc code asks these helpers before creating huge PUD/PMD mappings; both return true only under radix MMU because hash page table mode cannot handle large pages in vmalloc space.

State and persistence: No owned state; behavior depends on current MMU mode from `radix_enabled()`.

Dependencies and integration points: Depends on `asm/mmu.h`, `asm/page.h`, and generic vmalloc huge-vmap machinery.

Risks: Allowing huge vmalloc mappings under HPT can break address translation; disabling them under radix costs performance but is safe.

Test signals: Build huge-vmap configs, boot radix and HPT kernels, run vmalloc/ioremap stress and module loading tests.

Source read size: 24 lines, 554 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vmalloc.h -->
