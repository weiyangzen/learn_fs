<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S

Purpose: Provides the 32-bit BookE PR-mode low-level KVM guest entry, guest exit, copied exception handlers, and optional SPE register save/restore routines.

Important APIs/types/functions: Defines handler macros `KVM_HANDLER`, `KVM_DBG_HANDLER`, `KVM_HANDLER_ADDR`, the copied handler range `kvmppc_handlers_start/end`, `kvmppc_resume_host`, `__kvmppc_vcpu_run`, the handler address table `kvmppc_booke_handler_addr`, and `kvmppc_save_guest_spe()`/`kvmppc_load_guest_spe()` under `CONFIG_SPE`.

Control flow: At init, `booke.c` copies handler snippets into a 64 KiB IVPR-aligned page matching host IVOR offsets. Guest entry saves host nonvolatile registers and stack metadata, loads guest nonvolatiles, switches PID/PID1 and IVPR to the KVM handler page, reloads guest SPRG4-7 and volatile state, sets SRR0/SRR1 to guest PC/shadow MSR, clears stale debug status, and executes `rfi`. On guest exception, a tiny handler records the exit number and key registers, branches to `kvmppc_resume_host`, saves fault context and guest volatile state, restores host PID/IVPR/stack, calls `kvmppc_handle_exit()`, then either resumes the guest through a lightweight path or returns to C through a heavyweight exit.

State and persistence: Saves and restores host stack, LR, CR, r2, nonvolatile GPRs, guest GPRs, CTR, LR, XER, CR, PC, PID, PID1, IVPR, SPRG4-7, last instruction, DEAR, ESR, timing stamps, and SPE accumulator/EVRs. The assembly is the authoritative boundary between host thread state and guest vCPU state.

Dependencies and integration points: Depends on asm offsets, BookE interrupt numbers, KVM resume flags, PowerPC SPR definitions, copied-handler setup in `kvmppc_booke_init()`, and C exit handling in `kvmppc_handle_exit()`.

Risks: Any offset mismatch, missing register save, or wrong resume flag corrupts host or guest state. Switching IVPR before all memory references are guaranteed resident is dangerous, as noted by the source comment. Debug handler filtering has a small window where a breakpoint intended for guest context can fire in host context.

Test signals: PR-mode e500v2 guest boot, exception-heavy workloads, instruction emulation requiring nonvolatile reload, host interrupt delivery while in guest, SPE state tests, debug interrupt tests, and objdump/relocation inspection after asm-offset changes are important.

Source read size: 535 lines, 14587 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S -->
