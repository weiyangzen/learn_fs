<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h

Purpose: Defines x86 KVM paravirtual CPUID leaves, feature bits, KVM-specific MSRs, PV clock/steal-time structures, async page-fault data, PV EOI flags, MMU hypercall payloads, and GPA range mapping flags.

Important APIs/types/functions: `KVM_CPUID_SIGNATURE`, `KVM_SIGNATURE`, `KVM_CPUID_FEATURES`, `KVM_FEATURE_*`, `KVM_HINTS_REALTIME`, `MSR_KVM_*`, `struct kvm_steal_time`, `struct kvm_clock_pairing`, `KVM_ASYNC_PF_*`, `struct kvm_mmu_op_*`, `struct kvm_vcpu_pv_apf_data`, `KVM_PV_EOI_*`, and `KVM_MAP_GPA_RANGE_*`.

Control flow: Guests detect KVM through CPUID, enable paravirtual features via MSRs, receive PV clock/steal-time/async-PF state in shared pages, and issue KVM hypercalls for MMU ops or GPA encryption-state changes.

State and persistence behavior: Persistent guest-visible state includes shared steal-time pages, PV clock MSR addresses, async page-fault pages/tokens, PV EOI memory, migration readiness, and encrypted/decrypted GPA range requests.

Dependencies and integration points: Depends on Linux UAPI types and bit macros. Integrates with KVM guest drivers, pvclock, scheduler steal accounting, async page fault handling, PV TLB flush/IPI/yield, confidential guest memory conversion, and live migration readiness.

Risks and test signals: Risks include feature-bit mismatch, shared-page alignment mistakes, stale versioning, and async-PF delivery-mode confusion. Test KVM guest boot, pvclock stability, steal-time accounting, async page fault modes, PV EOI, PV TLB flush/send IPI, migration control, and encrypted memory range mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h -->
