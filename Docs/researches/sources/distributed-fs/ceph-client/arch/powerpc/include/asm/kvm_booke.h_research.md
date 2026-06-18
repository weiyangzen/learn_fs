# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke.h

Purpose: provides BookE KVM register access helpers, e500 LPID and `ehpriv` constants, fault-address access, floating-point register access, and magic-page capability detection.

Important APIs/types/functions: constants include `KVMPPC_NR_LPIDS`, `KVMPPC_INST_EHPRIV`, `EHPRIV_OC_SHIFT`, and `EHPRIV_OC_DEBUG`. Inline helpers get/set GPRs, CR, XER, CTR, LR, PC, FPRs, fault DAR, byte-swap requirements, and `kvmppc_supports_magic_page()`.

Control flow: KVM BookE code manipulates guest architectural state through these simple inline accessors. Magic-page mapping is only enabled for `CONFIG_KVM_E500V2`; `kvmppc_need_byteswap()` currently returns false with a note that TLB inspection would be needed.

State and persistence: all mutations target `vcpu->arch.regs`, `vcpu->arch.fp`, or `vcpu->arch.fault_dear`. No independent storage is allocated.

Dependencies and integration points: includes Linux KVM host definitions and is consumed by BookE emulation, MMIO, exception injection, and e500 magic-page code.

Risks: accessors assume register indexes are valid. The byte-swap helper is conservative/incomplete for guests using endian-changing mappings. FPR indexing depends on `TS_FPROFFSET`.

Test signals: boot e500/e500v2 guests, exercise MMIO load/store emulation, debug `ehpriv` traps, FP unavailable/save-restore paths, and magic-page setup only on e500v2 builds.
