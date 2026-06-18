<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c

### Purpose
`kprobes.c` implements MIPS kprobes and kretprobes. It replaces target instructions with breakpoints, single-steps a copied instruction in an executable slot, handles branch delay slots, and routes kretprobe returns through a trampoline.

### Important APIs, Types, And Functions
Architecture entry points include `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_exceptions_notify()`, `arch_prepare_kretprobe()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`. Internal handlers include `kprobe_handler()`, `post_kprobe_handler()`, `kprobe_fault_handler()`, `prepare_singlestep()`, `resume_execution()`, and `evaluate_branch_instruction()`.

### Control Flow
Preparation rejects LL/SC, compact branches, and branch-delay-slot targets; allocates an instruction slot; copies either the probed instruction or its delay-slot instruction; appends a second breakpoint; and saves the original opcode. A probe hit disables preemption, sets per-CPU current probe state, runs the pre-handler, redirects EPC to the copied instruction, and waits for the second breakpoint. Branch probes compute target EPC and may skip a NOP delay slot. Post handling runs the post-handler, resumes EPC, restores interrupt state, and clears or restores nested probe state.

### State, Persistence, And Dependencies
State is per-CPU `current_kprobe` and `kprobe_ctlblk`, patched kernel text, allocated instruction slots, saved opcodes, pt_regs EPC/status, and kretprobe instances. Dependencies include MIPS branch decoding, break exception notifications, text icache flushing, preempt control, and `probes-common.h`.

### Integration Points
The file integrates Linux kprobes core, die notifier values `DIE_BREAK`, `DIE_SSTEPBP`, and `DIE_PAGE_FAULT`, MIPS exception handling, and kretprobe trampoline registration.

### Risks
MIPS lacks native single-step, so correctness depends on SSOL slots and breakpoint recursion handling. Branch delay slots are fragile, LL/SC probes are refused to preserve atomicity, and faults during single-step must restore EPC/status without leaving preemption disabled.

### Test Signals
Run kprobes and kretprobes on ordinary instructions, branches with and without delay-slot work, nested probes, faulting copied instructions, module functions, and refused LL/SC or compact-branch targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/kprobes.c -->
