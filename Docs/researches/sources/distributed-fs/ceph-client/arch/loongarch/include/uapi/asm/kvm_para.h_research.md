<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h

Purpose: defines LoongArch KVM paravirtual CPUCFG leaves and feature bits.
Important APIs and types: provides `CPUCFG_KVM_BASE`, signature/feature leaves, `KVM_SIGNATURE`, and feature IDs for PV IPI, steal time, preempt, virtual EXTIOI, and user hypercalls.
Control flow: guests query CPUCFG leaves to discover KVM paravirtual features and enable optimized paths.
State and persistence: feature numbering is guest ABI.
Dependencies and integration: used by guest kernel paravirt code, KVM host emulation, and userspace VMM CPU model exposure.
Risks and test signals: mismatched feature IDs cause guest/host negotiation failures. Signals include KVM guest boot, paravirt IPI/steal-time tests, and CPUCFG ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm_para.h -->
