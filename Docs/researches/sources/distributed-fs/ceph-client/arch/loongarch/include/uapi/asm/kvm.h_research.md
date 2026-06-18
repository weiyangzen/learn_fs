<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h

Purpose: defines the LoongArch userspace KVM ABI.
Important APIs and types: declares `struct kvm_regs`, `struct kvm_fpu`, KVM register ID ranges for GPR/CSR/KVM/FPSIMD/CPUCFG/LBT, VM and VCPU feature attributes, IRQ line support, coalesced MMIO/dirty-log offsets, and debug flags.
Control flow: QEMU/VMMs use ioctls with these structures and register IDs to create VMs, configure VCPU state, inject IRQs, and control features.
State and persistence: structure layout and register IDs are stable userspace ABI for VM state migration and tooling.
Dependencies and integration: integrates with arch KVM implementation, LoongArch CSR/CPUCFG definitions, userspace VMMs, and migration formats.
Risks and test signals: ABI changes break VMM compatibility or live migration. Signals include KVM selftests, QEMU boot, register get/set round trips, and VM migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/kvm.h -->
