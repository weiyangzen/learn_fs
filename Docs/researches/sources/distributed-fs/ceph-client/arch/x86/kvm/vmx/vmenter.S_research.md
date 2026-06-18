# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmenter.S

## Purpose
Provides the low-level assembly path for VMX guest entry and exit, plus IRQ-off event trampolines and a VMREAD error trampoline for compiler configurations without asm-goto output.

## Important APIs, Types, And Functions
Main symbols are `__vmx_vcpu_run`, global inner label `vmx_vmexit`, `vmx_do_nmi_irqoff`, optional `vmread_error_trampoline`, and optional `vmx_do_interrupt_irqoff`. `VMX_DO_EVENT_IRQOFF` builds synthetic IRQ/NMI frames. Register offset macros map KVM vCPU register indices to array offsets. The run path consumes flags from `run_flags.h`.

## Control Flow
`__vmx_vcpu_run(vmx, regs, flags)` saves callee-saved host registers, saves arguments on the stack, calls `vmx_update_host_rsp()`, optionally writes guest SPEC_CTRL before any unsafe return/indirect branch, loads guest GPRs from `regs`, executes required VERW buffer clearing based on CPU alternatives and flags, and chooses VMLAUNCH or VMRESUME. Successful VM-entry resumes at `vmx_vmexit` via VMCS HOST_RIP. The exit path saves guest GPRs back to `regs`, sets return value 0, clears guest GPR values from host registers, fills the RSB, restores host SPEC_CTRL, clears branch history, restores host registers, and returns. VM-fail/fixup paths set return value 1, except reboot fixups can tolerate instruction failure.

## State And Persistence
Guest register state is persisted through the caller-provided `regs` array. Host state is protected on the stack and through `vmx_update_host_rsp()` and `vmx_spec_ctrl_restore_host()`. SPEC_CTRL and branch-history/RSB mitigation state are transient but security-critical. RSP is intentionally omitted from software GPR save/restore because hardware switches it.

## Dependencies And Integration Points
Depends on generated KVM assembly offsets, x86 alternatives, speculation mitigation macros, VMX instructions, run flags, and external C helpers. `vmx_do_nmi_irqoff` and `vmx_do_interrupt_irqoff` integrate with IRQ/NMI handling paths that must run with interrupts disabled.

## Risks
This is a high-risk security and correctness path. Stack layout must match argument/flag offsets. There must be no return or indirect branch between SPEC_CTRL handling and VM-entry. Guest registers must be cleared after exit to avoid speculative use. Mitigation alternatives must match CPU vulnerability requirements. Objtool unwind hints and synthetic interrupt frames must remain correct across 32-bit/64-bit and FRED/non-FRED configurations.

## Test Signals
VMX smoke tests, nested VMX launch/resume tests, VM-fail injection, objtool validation, noinstr validation, speculation mitigation selftests, NMI/IRQ exit stress, reboot/kexec paths, and register-corruption tests are key signals.
