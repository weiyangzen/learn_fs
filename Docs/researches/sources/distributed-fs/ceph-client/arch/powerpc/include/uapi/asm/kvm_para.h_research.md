<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h

Purpose: Defines PowerPC KVM paravirtual shared-page ABI and KVM hypercall token helpers.

Important APIs/types/functions: `struct kvm_vcpu_arch_shared`, magic `KVM_SC_MAGIC_R0`, `KVM_HCALL_TOKEN()`, `KVM_FEATURE_MAGIC_PAGE`, `KVM_MAGIC_FEAT_*`, and `MAGIC_PAGE_FLAG_NOT_MAPPED_NX`.

Control flow: Guest and host share selected vCPU state in a magic page; guest code uses advertised feature bits and KVM vendor hypercall tokens for paravirtual operations.

State and persistence: Shared page fields persist per vCPU and mirror scratch registers, exception state, segment registers, MAS registers, PIR, and high SPRGs.

Dependencies and integration points: Depends on ePAPR hcall definitions and KVM guest/host code. Documented by PowerPC KVM paravirtual docs.

Risks: Struct fields may only be appended; alignment and feature advertisement protect old guests. Inconsistent SPRG sharing can expose stale state to guest userspace.

Test signals: KVM guest boot with magic page enabled, paravirt feature probing, shared-register consistency tests, and migration compatibility checks.

Source read size: 85 lines, 2140 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm_para.h -->
