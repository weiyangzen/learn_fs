# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_mmu.h

## Purpose

`kvm_mmu.h` implements helpers for KVM stage page tables. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 151 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kvm_pte_t, kvm_ptw_ctx, kvm_set_pte, kvm_pte_* accessors, kvm_pgtable_offset, kvm_pgtable_addr_end, kvm_ptw_enter/exit. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_MMU_H__`, `KVM_MMU_CACHE_MIN_PAGES`, `KVM_PAGE_WRITEABLE`, `_KVM_FLUSH_PGTABLE`, `_KVM_HAS_PGMASK`, `kvm_pfn_pte`, `kvm_pte_pfn`, representative callable declarations or inline helpers `kvm_set_pte`, `kvm_pte_young`, `kvm_pte_huge`, `kvm_pte_dirty`, `kvm_pte_writeable`, `kvm_pte_mkyoung`, `kvm_pte_mkold`, `kvm_pte_mkdirty`, `kvm_pte_mkclean`, `kvm_pte_mkhuge`, `kvm_pte_mksmall`, `kvm_pte_mkwriteable`, and representative local types `unsigned`, `struct`, `int`, `kvm_ptw_ctx`. Direct includes seen in the header are `asm/pgalloc.h`, `asm/tlb.h`, `linux/kvm_host.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header used by KVM MMU fault handling, aging, hugepage and TLB flush paths. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: PTE flag translation, page-size levels and lock handling need MMU notifier and dirty-log tests. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
