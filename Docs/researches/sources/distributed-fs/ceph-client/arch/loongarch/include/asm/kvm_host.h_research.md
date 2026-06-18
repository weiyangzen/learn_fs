# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/kvm_host.h

## Purpose

`kvm_host.h` defines LoongArch KVM VM/vCPU architecture state. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 370 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: kvm_vm_stat, kvm_vcpu_stat, kvm_context, kvm_world_switch, kvm_arch, loongarch_csrs, kvm_vcpu_arch, feature helpers, TLB/MM fault and guest-entry prototypes. Symbol extraction from the file shows representative defines `__ASM_LOONGARCH_KVM_HOST_H__`, `__KVM_HAVE_ARCH_INTC_INITIALIZED`, `KVM_GET_IOC_CSR_IDX`, `KVM_GET_IOC_CPUCFG_IDX`, `KVM_MAX_VCPUS`, `KVM_MAX_CPUCFG_REGS`, `KVM_HALT_POLL_NS_DEFAULT`, `KVM_REQ_TLB_FLUSH_GPA`, `KVM_REQ_STEAL_UPDATE`, `KVM_REQ_PMU`, `KVM_REQ_AUX_LOAD`, `KVM_GUESTDBG_SW_BP_MASK`, representative callable declarations or inline helpers `readl_sw_gcsr`, `writel_sw_gcsr`, `kvm_guest_has_msgint`, `kvm_guest_has_fpu`, `kvm_guest_has_lsx`, `kvm_guest_has_lasx`, `kvm_guest_has_lbt`, `kvm_guest_has_pmu`, `kvm_get_pmu_num`, `kvm_vm_support`, `kvm_arch_pmi_in_guest`, `kvm_arch_vcpu_dump_regs`, and representative local types `kvm_vm_stat`, `kvm_vcpu_stat`, `kvm_arch_memory_slot`, `kvm_context`, `kvm_world_switch`, `kvm_phyid_info`, `kvm_phyid_map`, `kvm_arch`, `loongarch_csrs`, `emulation_result`. Direct includes seen in the header are `asm/inst.h`, `asm/kvm_dmsintc.h`, `asm/kvm_eiointc.h`, `asm/kvm_ipi.h`, `asm/kvm_mmu.h`, `asm/kvm_pch_pic.h`, `asm/loongarch.h`, `linux/cpumask.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header central integration point between generic KVM, LoongArch world switch, MMU, IRQ, timer, PMU and userspace ioctl state. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: state persistence is per-VM/vCPU; feature flags, CSR arrays and TLB flushing are high-risk. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
