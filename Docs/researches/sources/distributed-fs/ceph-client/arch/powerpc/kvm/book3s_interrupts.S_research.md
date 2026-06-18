# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_interrupts.S

Purpose: this assembly file is the high-memory PR KVM vCPU run loop for Book3S. It saves host state, loads guest nonvolatile state, copies volatile state into the shadow vCPU, enters the low-level trampoline, then returns from guest exits into C exit handling.

Important entry points: `__kvmppc_vcpu_run` is the exported run routine called by PR KVM C code. Internal labels `kvm_start_entry`, `kvm_start_lightweight`, `kvm_exit_loop`, `kvm_loop_heavyweight`, and `kvm_loop_lightweight` structure first entry, re-entry with nonvolatile reload, and lightweight re-entry.

Control flow: the entry path builds a switch frame, saves host LR/CR/nonvolatile GPRs, stores the vCPU pointer, and loads guest r14-r31. The lightweight path calls `kvmppc_copy_to_svcpu()`, restores the vCPU pointer, sets 64-bit host flags such as dcbz32 restore and guest SPRG3, then branches to `kvmppc_entry_trampoline()`. After lowmem/segment code exits the guest, the high-memory path stores the trap number, calls `kvmppc_copy_from_svcpu()`, restores host SPRG3, saves guest nonvolatile GPRs, and calls `kvmppc_handle_exit_pr()`. Return codes decide whether to exit to host, resume lightweight, or reload nonvolatile state before re-entry.

State and persistence: state is split between the stack frame, `struct kvm_vcpu`, PACA/shadow vCPU fields, SPRG3, and nonvolatile guest GPR slots. The file does not allocate memory; it preserves ABI state across guest execution.

Dependencies and integration: it depends on generated asm offsets, PPC ABI mode, `book3s_segment.S` via the trampoline target, and C helpers `kvmppc_copy_to_svcpu()`, `kvmppc_copy_from_svcpu()`, and `kvmppc_handle_exit_pr()`. It is invoked from `kvmppc_vcpu_run_pr()` in `book3s_pr.c`.

Risks: this code is register- and ABI-sensitive. A wrong offset or missed save/restore can corrupt host state or guest state. Endianness conversion for shared SPRG3 must match the shared page mode. The lightweight/heavyweight distinction matters because `RESUME_GUEST_NV` requires nonvolatile guest GPRs to be reloaded.

Test signals: run PR guests through repeated exits, PAPR hcalls, SPRG3 shared-page updates, both endian modes, dcbz32 host flag cases, and paths returning `RESUME_GUEST` versus `RESUME_GUEST_NV`. Failures usually appear as corrupted nonvolatile registers, bad trap numbers, or host instability after guest exit.
