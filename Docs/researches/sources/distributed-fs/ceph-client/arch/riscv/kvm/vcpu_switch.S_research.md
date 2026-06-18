<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S

## Purpose
`vcpu_switch.S` is the low-level RISC-V KVM world-switch and floating-point save/restore code. It moves execution between host supervisor context and guest virtual supervisor context.

## Important APIs, Types, And Functions
Macros save and restore host/guest GPRs and CSRs: `SAVE_HOST_GPRS`, `SAVE_HOST_AND_RESTORE_GUEST_CSRS`, `RESTORE_GUEST_GPRS`, `SAVE_GUEST_GPRS`, `SAVE_GUEST_AND_RESTORE_HOST_CSRS`, and `RESTORE_HOST_GPRS`. Exported entry points are `__kvm_riscv_switch_to`, `__kvm_riscv_nacl_switch_to`, `__kvm_riscv_unpriv_trap`, and F/D floating-point save/restore functions under `CONFIG_FPU`.

## Control Flow
The normal switch saves host registers to `struct kvm_vcpu_arch`, swaps SSTATUS/STVEC/SEPC/SSCRATCH to guest values, restores guest GPRs, and enters with `sret`. Trap return lands on the host resume label, saves guest GPR/CSR state, restores host CSR/GPR state, and returns to C. NaCl switch uses an SBI ECALL instead of `sret`. The unpriv trap handler records trap CSRs and advances SEPC by one 4-byte instruction.

## State And Persistence
The file mutates only in-memory CPU context fields and architectural CSRs. FP helpers serialize FCSR and all F registers into the KVM context.

## Dependencies And Integration Points
It depends on asm offset definitions matching `struct kvm_vcpu_arch`, CSR numbers, RISC-V calling convention, and KVM C code that prepares/load/saves optional FPU/vector state around this switch.

## Risks
Any offset drift corrupts host or guest state. The unpriv trap handler assumes a 4-byte instruction. CSR ordering around SSTATUS/STVEC/SSCRATCH is critical for safe trap return. FP helpers must restore SSTATUS after temporarily enabling FS.

## Test Signals
Signals include guest boot under interrupt load, nested-acceleration path tests, FPU-heavy guest workloads, unprivileged emulation fault tests, and objtool/assembler checks against generated offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S -->
