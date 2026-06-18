## sources/distributed-fs/ceph-client/arch/arm/probes/uprobes/core.c

### Purpose
Provides the ARM architecture glue for generic uprobes: breakpoint opcode installation, instruction analysis, XOL copy/pre/post handling, return-probe LR hijacking, and undefined-instruction trap registration.

### Important APIs, Types, And Functions
Important entry points include `is_swbp_insn`, `set_swbp`, `arch_uprobe_ignore`, `arch_uprobe_skip_sstep`, `arch_uretprobe_hijack_return_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_copy_ixol`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_abort_xol`, `uprobe_get_swbp_addr`, and `arch_uprobes_init`.

### Control Flow
Analysis rejects unaligned/Thumb addresses, decodes the ARM instruction, prepares one copied instruction plus an ARM single-step trap, and derives a condition-coded software breakpoint. At trap time `uprobe_trap_handler()` distinguishes breakpoint and single-step opcodes, then calls generic pre/post single-step notifiers with local IRQs disabled. XOL setup saves the previous thread trap number, marks it as `UPROBE_TRAP_NR`, and redirects `ARM_pc`; post-XOL restores the trap number and advances to the original instruction plus four bytes.

### State, Persistence, And Dependencies
Per-probe state includes `bpinsn`, `ixol`, `simulate`, and decoded `asi` handlers. Per-task state uses `current->utask`, `autask.saved_trap_no`, and the XOL/original virtual addresses. Dependencies include undefined-instruction hooks, highmem mapping, cache flush via `flush_uprobe_xol_access`, and generic uprobe notifier paths.

### Integration Points
Registers `undef_hook` entries at `device_initcall`, making ARM undefined-instruction traps the uprobe breakpoint and single-step mechanism. It interacts with generic return probes by replacing `ARM_lr` with a trampoline address.

### Risks
Unsupported Thumb addresses return `-EINVAL`; mixed ARM/Thumb probe expectations will fail. Trap-number bookkeeping is context-sensitive; bad restore paths can misreport later exceptions. Cache flushing and XOL page mapping must be correct for self-modifying executable code.

### Test Signals
Run uprobes and uretprobes on ARM userspace functions, including conditional instructions and simulated instructions. Fault inside XOL to validate abort/trap detection. Confirm cache coherency on VIPT/noncoherent ARM targets.
