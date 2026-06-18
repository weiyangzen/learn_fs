<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h

## Purpose
Defines Xtensa kernel virtual memory layout: page-table region, KSEG cached/bypass mappings, KIO mappings, KSEG physical base, and kernel stack size.

## Important APIs, Types, And Functions
Key macros are `XCHAL_PAGE_TABLE_VADDR`, `XCHAL_PAGE_TABLE_SIZE`, `XCHAL_KSEG_CACHED_VADDR`, `XCHAL_KSEG_BYPASS_VADDR`, `XCHAL_KSEG_SIZE`, `XCHAL_KSEG_ALIGNMENT`, `XCHAL_KSEG_TLB_WAY`, `XCHAL_KIO_TLB_WAY`, `XCHAL_KSEG_PADDR`, `XCHAL_KIO_CACHED_VADDR`, `XCHAL_KIO_BYPASS_VADDR`, `XCHAL_KIO_DEFAULT_PADDR`, `XCHAL_KIO_SIZE`, `XCHAL_KIO_PADDR`, `xtensa_get_kio_paddr`, `KERNEL_STACK_SHIFT`, and `KERNEL_STACK_SIZE`.

## Control Flow
Preprocessor branches select one of the MMU KSEG layouts and enforce physical-base alignment. For some OF configurations, KIO physical base is a runtime variable exposed by `xtensa_get_kio_paddr`.

## State And Persistence
No owned state except external `xtensa_kio_paddr` in dynamic KIO configurations. Constants define persistent virtual memory layout.

## Dependencies And Integration Points
Depends on Kconfig layout choices, core MMU features, OF, page tables, `page.h`, `io.h`, and MMU initialization.

## Risks And Edge Cases
Misaligned KSEG physical base is compile-time fatal. Wrong layout breaks `__pa`/`__va`, ioremap, highmem, and TLB setup. KASAN increases stack size.

## Test Signals
Compile all KSEG layout choices, boot OF and non-OF KIO configurations, test `__pa`/`__va`, MMIO, and stack overflow/KASAN builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kmem_layout.h -->
