<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h

Purpose: Defines the extensive PowerPC KVM userspace ABI for vCPU registers, special registers, debug controls, TCE/RMA/RTAS/MMU setup, one-reg IDs, interrupt controllers, XIVE, and PPC-specific VM capabilities.

Important APIs/types/functions: Feature selectors `__KVM_HAVE_*`, `struct kvm_regs`, `struct kvm_sregs`, FPU/debug structs, interrupt constants, CPU type IDs, SPAPR TCE/RMA/RTAS structs, BookE TLB structs, HTAB/MMU/radix/CPU-character structs, hundreds of `KVM_REG_PPC_*` one-reg IDs, XICS/XIVE device groups, `struct kvm_ppc_xive_eq`, PV info, SMMU info, and HPT resize structures.

Control flow: Userspace VMMs issue KVM ioctls using these structs and register IDs to create devices, save/restore vCPU state, configure MMU/TCE/interrupts, inject interrupts, expose paravirtual info, and migrate machines.

State and persistence: Defines persistent VM/vCPU ABI state: GPRs, SPRs, MMU state, debug breakpoints, interrupt-controller state, event queues, page-size geometry, and migration streams.

Dependencies and integration points: Depends on Linux types and generic KVM ioctls. Integrated by QEMU, kvmtool, KVM Book3S/BookE implementations, XICS/XIVE device models, and migration tooling.

Risks: This is a migration and virtualization ABI; field padding, feature bits, one-reg sizes, and update semantics must not change incompatibly. Reserved fields must be preserved by userspace.

Test signals: KVM selftests for PPC, QEMU boot/migration across Book3S/BookE, one-reg get/set round trips, XICS/XIVE interrupt tests, TCE/MMU setup tests, and ABI structure size checks.

Source read size: 769 lines, 25469 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/kvm.h -->
