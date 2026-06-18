## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry.S` is the low-level ARM64 exception,
return, context-switch, IRQ-stack, KPTI trampoline, branch-history-mitigation, and SDEI assembly
entry code. It saves architectural state into `pt_regs`, switches between user/kernel execution
contexts, installs mitigation state, and dispatches into `entry-common.c`.

### Important APIs, Types, And Functions
Core macros include `kernel_ventry`, `kernel_entry`, `kernel_exit`, `entry_handler`,
`apply_ssbd`, MTE tag-fault/GCR helpers, `tramp_map_kernel`, `tramp_unmap_kernel`, `tramp_ventry`,
and vector-generation macros. Major symbols are `vectors`, `__bad_stack`, generated
`el*_*_*` entry stubs, `ret_to_kernel`, `ret_to_user`, `tramp_vectors`, `tramp_exit`,
`__bp_harden_el1_vectors`, `cpu_switch_to`, `ret_from_fork`, `call_on_irq_stack`, and SDEI symbols
`__sdei_asm_entry_trampoline`, `__sdei_asm_exit_trampoline`, `__sdei_asm_handler`, and
`__sdei_handler_abort`.

### Control Flow
Each vector slot runs `kernel_ventry`, allocates `pt_regs`, checks for stack overflow without
clobbering GPRs, and branches to an EL/handler-specific stub. `kernel_entry` saves GPRs, clears user
GPRs on EL0 entry, swaps `sp_el0` to the current task, disables pending single-step state, checks
MTE async tag faults, installs kernel pointer-auth keys, applies SSBD mitigation, sets kernel MTE
GCR, loads shadow call stack state, records ELR/SPSR/LR/SP metadata, handles software PAN, and saves
PMR for pseudo-NMI. Generated entry handlers call the matching C handler and branch to kernel or user
return.

`kernel_exit` restores PMR, ELR/SPSR, software PAN/TTBR0 state, user SP, pointer-auth keys, MTE user
GCR, SSBD state, all registers, KPTI trampoline exit if needed, speculative-load/TLBI workarounds,
and finally `eret`. KPTI trampoline vectors map the kernel, apply optional BHB mitigations, install
real vectors, and jump into the full vector table. `cpu_switch_to` saves/restores callee-saved task
context, updates `sp_el0`, pointer-auth keys, and shadow call stack. `ret_from_fork` finishes new
tasks and returns through user exit. `call_on_irq_stack` switches to per-CPU IRQ and shadow IRQ
stacks before invoking a C IRQ handler. SDEI assembly saves firmware-preserved register state,
switches to SDEI stacks, calls C SDEI handling, and completes/resumes through SMC/HVC.

### State, Persistence, And Dependencies
State is architectural: GPRs, ELR/SPSR, SPs, VBAR, TTBR1, PMR, MDSCR step state, MTE TFSR/GCR,
pointer-auth keys, shadow call stack pointers, task `thread_info`, per-CPU entry task/vector/IRQ/SDEI
stacks, and saved `pt_regs`. Dependencies include generated asm offsets, ARM64 alternatives,
exception C handlers, MMU/KPTI layout, Spectre SSBD/BHB mitigation callbacks, MTE, pointer
authentication, software PAN, pseudo-NMI/GIC priority masking, shadow call stack, stackleak,
scheduler context switch layout, and SDEI firmware ABI.

### Integration Points
This is the hardware-facing entrance to `entry-common.c`, scheduler context switching, IRQ handling,
fork return, KPTI vector selection from `cpufeature.c`, Spectre mitigation code, SDEI firmware
events, stack overflow panic handling, and per-task security state. All kernel subsystems,
including Ceph client code, depend on these paths for correct syscall, interrupt, fault, and
preemption behavior.

### Risks
The vector slot size, stack overflow arithmetic, `pt_regs` offsets, and register restore ordering
are ABI- and hardware-critical. Any instruction after user register restore can leak or clobber user
state. Mitigation ordering affects Spectre/KPTI/PAN/MTE/PAuth security. Incorrect PMR or DAIF
handling can lose interrupts or break pseudo-NMI semantics. SDEI and IRQ-stack switching must
preserve shadow call stack state. Assembly and C structure layout drift is especially dangerous.

### Test Signals
Boot tests with KPTI on/off, Spectre BHB/SSBD mitigation variants, pseudo-NMI, MTE, pointer auth,
shadow call stack, stackleak, software PAN, SDEI, IRQ flood tests, syscall/fault stress,
context-switch stress, fork/exec tests, stack-overflow tests, CPU hotplug, and objdump validation of
vector slot size and alternative patch sites are the strongest signals.
