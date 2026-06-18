## sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/uprobes.c` implements MIPS architecture support for uprobes. It validates probed instructions, prepares out-of-line execution slots, handles breakpoint die notifications, restores EPC after XOL, supports return probes, and copies instruction slots with icache flushing.

### Important APIs, Types, And Functions
Important functions are `arch_uprobe_analyze_insn()`, `is_trap_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_xol_was_trapped()`, `arch_uprobe_exception_notify()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_hijack_return_addr()`, `arch_uprobe_copy_ixol()`, `uprobe_get_swbp_addr()`, and `arch_uprobe_skip_sstep()`.

### Control Flow
Analysis rejects unaligned addresses, effectively disallows MIPS16/microMIPS, rejects compact branches, and builds an XOL slot containing either the instruction or its delay-slot companion followed by an XOL breakpoint. Pre-XOL computes the resume EPC, including branch delay behavior, saves `thread.trap_nr`, sets a sentinel, and redirects EPC to the XOL page. Post-XOL restores trap number and EPC. Die notifier callbacks intercept uprobe and XOL breakpoints for user mode and route them to generic uprobe pre/post handlers.

### State, Persistence, And Dependencies
State is per-uprobe `arch_uprobe` data (`insn`, `ixol`, `resume_epc`) and per-task `utask->autask.saved_trap_nr`. The return probe path mutates register `$31`. Dependencies include `asm/branch.h`, MIPS trap break codes, generic uprobes, highmem page mapping, icache flushing, and die notifier values produced by `traps.c`.

### Integration Points
`traps.c` identifies `BRK_UPROBE` and `BRK_UPROBE_XOL` and emits die notifications consumed here. Generic uprobes calls these architecture hooks. Signal and fatal trap handling consult `arch_uprobe_xol_was_trapped()` and abort hooks.

### Risks
Delay-slot and branch resume computation are the highest-risk areas. Compact branches are explicitly unsupported. XOL copying must flush icache or tasks may execute stale instructions. Return probe hijacking must preserve the original RA. Misidentifying trap instructions can prevent probing or recursively trap.

### Test Signals
Probe regular instructions, branch-with-delay-slot instructions, rejected compact branches, rejected unaligned or MIPS16/microMIPS addresses, XOL breakpoint handling, XOL abort on signal, return probes, and icache coherency after installing slots.
