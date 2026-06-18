# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/kvm.h

## Purpose
Defines the arm64 userspace KVM ABI copied into tools: vCPU register layout, vCPU feature bits, VGIC control attributes, SVE register IDs, firmware pseudo-registers, PMU/timer/pvtime controls, PSCI constants, SMCCC filtering, and feature-ID writable-mask query structures.

## Important APIs, Types, and Functions
Important types include `struct kvm_regs`, `kvm_vcpu_init`, `kvm_guest_debug_arch`, `kvm_debug_exit_arch`, `kvm_sync_regs`, `kvm_pmu_event_filter`, `kvm_vcpu_events`, `kvm_arm_copy_mte_tags`, `kvm_arm_counter_offset`, `kvm_smccc_filter`, and `reg_mask_range`. Register-id helpers include `KVM_REG_ARM_CORE_REG()`, `ARM64_SYS_REG()`, SVE `KVM_REG_ARM64_SVE_*` macros, and firmware bitmap register macros.

## Control Flow, State, and Persistence
This header is declarative ABI. Userspace fills structs and numeric IDs for ioctls; KVM persists guest state in kernel, while tools only encode/decode the contract. Some values, notably swapped virtual timer CVAL/CNT IDs, are intentionally frozen ABI rather than architectural encodings.

## Dependencies and Integration Points
Depends on `linux/psci.h`, `linux/types.h`, arm64 ptrace state, and SVE context constants. Integrates with QEMU/kvmtool/perf tests and kernel KVM ioctls for vCPU init, one-reg access, interrupt injection, device attributes, migration, and hypercall exit routing.

## Risks and Test Signals
Risks are ABI breakage from changing padding, reserved fields, frozen register IDs, SVE slice sizing, or feature bitmap numbering. Test signals include userspace KVM build coverage, `KVM_GET/SET_ONE_REG` round trips for timers/SVE/FW regs, vCPU feature negotiation, VGIC device-attribute ioctls, and migration struct compatibility tests.
