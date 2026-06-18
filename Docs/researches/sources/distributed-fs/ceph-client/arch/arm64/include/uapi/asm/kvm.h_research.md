<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h` defines the arm64 KVM userspace ABI: register layouts, vCPU initialization features, VGIC addresses, debug state, device attributes, MTE tag copy, counter offsets, and one-reg encodings. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARM_KVM_H__`, `KVM_SPSR_EL1`, `KVM_SPSR_SVC`, `KVM_SPSR_ABT`, `KVM_SPSR_UND`, `KVM_SPSR_IRQ`, `KVM_SPSR_FIQ`, `KVM_NR_SPSR`, `__KVM_HAVE_IRQ_LINE`, `__KVM_HAVE_VCPU_EVENTS`, `KVM_COALESCED_MMIO_PAGE_OFFSET`, `KVM_DIRTY_LOG_PAGE_OFFSET`, `KVM_ARM_TARGET_AEM_V8`, `KVM_ARM_TARGET_FOUNDATION_V8`, `KVM_ARM_TARGET_CORTEX_A57`, `KVM_ARM_TARGET_XGENE_POTENZA`, `KVM_ARM_TARGET_CORTEX_A53`, `KVM_ARM_TARGET_GENERIC_V8`, `KVM_ARM_NUM_TARGETS`, `KVM_ARM_DEVICE_TYPE_SHIFT`, `KVM_ARM_DEVICE_TYPE_MASK`, `KVM_ARM_DEVICE_ID_SHIFT`, `KVM_ARM_DEVICE_ID_MASK`, `KVM_ARM_DEVICE_VGIC_V2`, `KVM_VGIC_V2_ADDR_TYPE_DIST`, `KVM_VGIC_V2_ADDR_TYPE_CPU`, `KVM_VGIC_V2_DIST_SIZE`, `KVM_VGIC_V2_CPU_SIZE`, and 169 more; types: `kvm_regs`, `user_pt_regs`, `user_fpsimd_state`, `kvm_vcpu_init`, `kvm_sregs`, `kvm_fpu`, `kvm_guest_debug_arch`, `kvm_debug_exit_arch`, `kvm_sync_regs`, `kvm_pmu_event_filter`, `kvm_vcpu_events`, `kvm_arm_copy_mte_tags`, `kvm_arm_counter_offset`, `kvm_smccc_filter_action`, `kvm_smccc_filter`, `reg_mask_range`. The file is 564 lines / 18178 bytes. Direct includes are `linux/psci.h`, `linux/types.h`, `asm/ptrace.h`, `asm/sve_context.h`.

### Control Flow
Userspace VMMs pass these structures through KVM ioctls to create vCPUs, configure interrupts/timers/PMU/SVE/ptrauth/nested virtualization, inspect exits, and synchronize device IRQ levels.

### State, Persistence, And Dependencies
Notable global/static state symbols are `regs`, `fp_regs`. These structures are the persistent ABI between VMM processes and in-kernel KVM vCPU/VM state. The header must remain backwards compatible. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout, alignment, or constant changes can break QEMU, crosvm, cloud hypervisors, migration streams, or debug tools.

### Test Signals
Run KVM selftests, QEMU boot tests with GICv2/v3, PMU, SVE, MTE, ptrauth, nested virtualization, and ABI compile checks against userspace VMMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/kvm.h -->
