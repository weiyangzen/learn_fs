<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c

## Purpose
`vcpu_sbi_system.c` implements the SBI System Suspend extension wrapper for KVM.

## Important APIs, Types, And Functions
`kvm_sbi_ext_susp_handler()` handles `SBI_EXT_SUSP_SYSTEM_SUSPEND`. `vcpu_sbi_ext_susp` registers the extension as default-disabled.

## Control Flow
The handler validates suspend-to-RAM type, verifies the guest is in supervisor mode, checks the resume address GPA is valid, requires all other vCPUs to be stopped, stores reset state for the current vCPU, and forwards the actual suspend operation to userspace.

## State And Persistence
It records current-vCPU reset pc and opaque argument through shared reset-state helpers. It otherwise relies on userspace for suspend persistence and platform behavior.

## Dependencies And Integration Points
The file integrates SBI dispatch, KVM guest address validation, HSM stopped-state checks, reset-state helpers, and `KVM_EXIT_RISCV_SBI` forwarding.

## Risks
Suspend is default-disabled because userspace policy is required. Incorrect privilege, address, or stopped-vCPU checks could let a guest enter an impossible resume state. Forwarded calls depend on VMM support.

## Test Signals
Tests should verify disabled probe behavior, enable-and-forward exits, invalid type/address/privilege errors, and denial when another vCPU is still running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c -->
