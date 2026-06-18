# sources/distributed-fs/ceph-client/arch/arm64/kvm/guest.c

## Purpose

This file implements arm64 KVM userspace ABI helpers for vCPU register enumeration, one-register get/set, event injection/query, guest debug setup, vCPU attribute dispatch, target CPU reporting, and MTE tag copy.

## Important APIs, Types, And Functions

Key public APIs are `kvm_arm_num_regs()`, `kvm_arm_copy_reg_indices()`, `kvm_arm_get_reg()`, `kvm_arm_set_reg()`, `__kvm_arm_vcpu_get_events()`, `__kvm_arm_vcpu_set_events()`, `kvm_arch_vcpu_ioctl_set_guest_debug()`, `kvm_arm_vcpu_arch_{set,get,has}_attr()`, and `kvm_vm_ioctl_mte_copy_tags()`. Internal helpers validate core-reg offsets, SVE vector-length bitmaps, SVE register regions, and event commitment.

## Control Flow

Register ID handling first validates the arm64 namespace, then dispatches to core, firmware, SVE, or sysreg handlers. SVE register access requires a finalized SVE vCPU except for setting vector lengths before finalization. Event setting immediately commits external data aborts and may inject SError with or without ESR. MTE tag copying locks memslots, walks pages by GFN, rejects device memory, serializes dirty logging restrictions, and copies tags between user buffers and page memory.

## State And Persistence Behavior

The file reads and writes `vcpu->arch.ctxt`, FPSIMD fields, `sve_state`, `sve_max_vl`, event/exception flags, `guest_debug`, external debug state, PMU/timer/pvtime attributes, and MTE page tag state. User copies are direct ABI transfers; register setters mutate live saved vCPU state.

## Dependencies And Integration Points

It depends on sysreg table helpers, firmware register helpers, PMU/timer/pvtime devices, FPSIMD/SVE layout macros, debug tracepoints, RAS/SEA injection, MTE tag APIs, page and memslot helpers, and nested virtualization checks for EL2 PSTATE validity.

## Risks And Test Signals

Important risks are off-by-one register-list bounds, accepting invalid PSTATE modes, SVE access before finalization, missing nospec bounds on SVE offsets, dirty logging conflicts during tag writes, partial tag-copy return values, and stale exception state after userspace injection. Test signals include `KVM_GET_REG_LIST` order, SVE VLS validation, AArch32 narrowing on pstate writes, SError/SEA event round trips, guest debug exits, and MTE copy over multiple pages or hugetlb pages.
