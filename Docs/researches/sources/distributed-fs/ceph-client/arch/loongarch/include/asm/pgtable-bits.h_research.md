<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h

Purpose: defines the LoongArch software and hardware page-table bit layout used by the MMU, generic memory management, swap encoding, huge pages, and protection macros.
Important APIs and types: exports `_PAGE_*` bit constants for valid, dirty, present, write, global, huge, protnone, special, non-readable, non-executable, accessed, modified, present-invalid, and swap-exclusive state. It also defines cacheability encodings such as `_CACHE_CC`, `_CACHE_SUC`, `_CACHE_WUC`, `_CACHE_UC`, page protection presets like `PAGE_KERNEL`, `PAGE_SHARED`, `PAGE_READONLY`, `PAGE_NONE`, and `__P*`/`__S*` protection tables.
Control flow: there is no runtime flow; the header is consumed at compile time by `pgtable.h`, TLB code, KVM MMU helpers, and architecture memory setup. The conditional layout differs for 32-bit versus 64-bit and for `CONFIG_ARCH_HAS_PTE_SPECIAL`.
State and persistence: the bit definitions are the persistent in-memory ABI of LoongArch PTEs and PMDs. Any mismatch changes how page tables encode permissions, dirty/accessed status, swap entries, and huge-page global bits.
Dependencies and integration: depends on `asm/loongarch.h` cache constants and feeds Linux generic MM APIs through pgprot and pte helpers. It also aligns with hardware CSR/TLB semantics and user-visible behavior such as NX and write protection.
Risks and test signals: risky changes include overlapping bits, stale `_PAGE_CHG_MASK`, or incorrect cacheability flags. Build coverage, boot under page-fault stress, mmap/mprotect/swap tests, THP tests, and KVM page-table tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/pgtable-bits.h -->
