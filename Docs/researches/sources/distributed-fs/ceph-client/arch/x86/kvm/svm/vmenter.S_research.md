# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/vmenter.S

## Purpose
`vmenter.S` contains the low-level AMD SVM guest-entry assembly routines. It performs register save/restore, VMLOAD/VMSAVE/VMRUN sequencing, SPEC_CTRL switching, CPU-buffer/RSB/RET mitigations, and special SEV-ES entry behavior. It is placed in `.noinstr.text` because it runs in a fragile IRQ/guest-state transition context where instrumentation would be unsafe.

## Important APIs, Types, and Functions
Exported symbols:

- `__svm_vcpu_run(struct vcpu_svm *svm, bool spec_ctrl_intercepted)` runs a normal SVM vCPU.
- `__svm_sev_es_vcpu_run(struct vcpu_svm *svm, bool spec_ctrl_intercepted, struct sev_es_save_area *hostsa)` runs an SEV-ES vCPU on x86_64 when `CONFIG_KVM_AMD_SEV` is enabled.

Important macros:

- `RESTORE_GUEST_SPEC_CTRL` and `RESTORE_GUEST_SPEC_CTRL_BODY` restore guest `MSR_IA32_SPEC_CTRL` immediately before VMRUN when hardware does not virtualize it.
- `RESTORE_HOST_SPEC_CTRL` and `RESTORE_HOST_SPEC_CTRL_BODY` read guest SPEC_CTRL if it was not intercepted and restore the host's per-CPU SPEC_CTRL value after VMEXIT.
- `SVM_CLEAR_CPU_BUFFERS` emits CPU-buffer clearing when `X86_FEATURE_CLEAR_CPU_BUF_VM` is active.
- `FILL_RETURN_BUFFER`, `UNTRAIN_RET_VM`, and `RET` integrate x86 speculation mitigations.
- Offset macros such as `VCPU_RCX`, `SVM_vmcb01_pa`, and `SVM_current_vmcb` use generated asm offsets to access `struct vcpu_svm` and nested fields.

## Control Flow
Normal SVM path:

1. Save host callee-saved registers on the stack.
2. Push `spec_ctrl_intercepted`, per-CPU host save area physical address, and `svm` for post-exit recovery.
3. Put `svm` in the canonical argument register and restore guest SPEC_CTRL if required.
4. `vmload` VMCB01 to load hardware-managed guest state shared by VMCB01/VMCB02.
5. Load the current VMCB physical address, then load guest GPRs from `svm->vcpu.arch.regs` except RAX/RSP, which hardware switches through the VMCB.
6. Clear CPU buffers if required.
7. Execute `vmrun`.
8. On exit, recover `svm`, save guest GPRs back to `vcpu.arch.regs`, `vmsave` VMCB01, and `vmload` the host save area to restore host GSBASE and related state.
9. Fill the return buffer, restore host SPEC_CTRL, untrain returns, zero guest GPR values from registers, pop saved host registers, and return.

Fault labels around VMLOAD/VMRUN/VMSAVE/host VMLOAD check `virt_rebooting`; if a virtualization instruction faults during reboot, execution resumes after the instruction, otherwise `ud2` terminates the path. Exception-table entries route faults to these labels.

SEV-ES path:

1. Save nonvolatile host GPRs and needed volatile arguments into the SEV-ES host save area because SEV-ES hardware restores most GPRs on VMEXIT but does not save all host values on VMRUN.
2. Restore guest SPEC_CTRL if required.
3. Load current VMCB physical address.
4. Clear CPU buffers and execute `vmrun`.
5. On exit, fill RSB, restore host SPEC_CTRL, untrain returns, end frame, and return.

The SEV-ES path does not manually load/save guest GPRs because encrypted guest state is protected and hardware/VMSA mechanisms own it.

## State and Persistence Behavior
The assembly routine mutates:

- Guest general-purpose registers in `vcpu->arch.regs` for normal SVM.
- VMCB01 save state through `vmload`/`vmsave`.
- Current VMCB execution state through `vmrun`.
- Per-CPU host save area state through `vmload` after VMEXIT.
- `svm->spec_ctrl` if guest SPEC_CTRL was not intercepted.
- SEV-ES host save area GPR slots.

It deliberately clears most host registers after VMEXIT to avoid speculative use of guest-controlled values. It does not allocate memory or persist filesystem data.

## Dependencies and Integration Points
This file depends on generated offsets from `asm-offsets.h` and `kvm-asm-offsets.h`, SVM structure layout from `svm.h`, x86 speculation mitigation macros, x86 exception tables, and the C wrapper `svm_vcpu_enter_exit()`. The C code is responsible for entering the correct IRQ/GIF/guest-state context before calling these symbols and for interpreting VMCB exit information afterward.

## Risks and Edge Cases
Risks:

- Structure offset drift between C and assembly can corrupt guest/host registers; generated offsets and build checks are critical.
- No indirect branches or returns may occur between guest SPEC_CTRL restore and VMRUN; the comments explicitly call out RSB-underflow risk.
- Host SPEC_CTRL restore must read guest SPEC_CTRL only if the MSR was not intercepted; otherwise `svm->spec_ctrl` already contains the last known value.
- Guest register zeroing after VMEXIT is defensive against speculation and must not clobber values before they are saved.
- Fault recovery around SVM instructions is only acceptable for reboot paths; unexpected faults intentionally hit `ud2`.
- SEV-ES has different GPR ownership rules; applying normal SVM register save/restore would violate protected-state semantics.

## Test Signals
Test signals include successful VM entry/exit under normal SVM and SEV-ES, no objtool/noinstr warnings, no exception-table failures outside reboot, correct guest GPR preservation across exits, SPEC_CTRL correctness under guest writes and intercept-pass-through modes, and mitigation-sensitive tests for RSB/RET/CLEAR_CPU_BUF behavior.
