<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h

Purpose: Adapts generic TLB gather to PowerPC MMU behavior.

Important APIs/types/functions: `__tlb_remove_tlb_entry()`, `tlb_flush()`, `tlb_needs_table_invalidate()`, and local/thread/core MM helpers. Source-visible declarations include: #define _ASM_POWERPC_TLB_H; static inline void __tlb_remove_tlb_entry(struct mmu_gather *tlb, pte_t *ptep,; #define __tlb_remove_tlb_entry __tlb_remove_tlb_entry; #define tlb_flush tlb_flush; extern void tlb_flush(struct mmu_gather *tlb);; #define tlb_needs_table_invalidate() radix_enabled(); static inline void __tlb_remove_tlb_entry(struct mmu_gather *tlb, pte_t *ptep,; static inline int mm_is_core_local(struct mm_struct *mm).

Control flow: MM teardown batches PTE removals and later flushes translations with radix/hash-specific invalidation behavior. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: TLB gather state is caller-owned; hardware TLB state is invalidated by backend calls. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/pgtable.h>, #include <asm/page.h>, #include <asm/mmu.h>, #include <linux/pagemap.h>, #include <asm-generic/tlb.h>. Integrated with generic MM, radix/hash MMU, page-table freeing, and memory reclaim.

Risks: under-invalidating leaves stale translations while table invalidation requirements differ by MMU. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 93 lines, 2322 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tlb.h -->
