## sources/distributed-fs/ceph-client/arch/s390/kernel/uprobes.c

Purpose: Implements s390 architecture support for uprobes and uretprobes, including out-of-line execution setup, post-single-step fixups, PER interaction, and emulation of PC-relative RIL instructions that cannot safely execute from the XOL area.

Important APIs and functions: `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_exception_notify()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, and `arch_uprobe_skip_sstep()`. Key helpers include `check_per_event()`, `sim_stor_event()`, and `handle_insn_ril()`.

Control flow: Pre-XOL rejects 24/31-bit address modes, clears PER trap state, saves PSW PER and int-code, marks the regs with a synthetic trap number, redirects PSW to the XOL slot, sets `TIF_UPROBE_SINGLESTEP`, and updates control registers. Post-XOL restores flags, fixes PSW or return-register addresses based on decoded probe fixup bits, handles branch-not-taken correction, and re-triggers PER events if emulated execution matched user PER controls. Exception notifier maps breakpoint/singlestep die events into uprobe pre/post handlers. RIL emulation computes the original PC-relative target, performs aligned user loads/stores/compares, simulates storage alteration PER, advances PSW, and reports appropriate synthetic traps on faults.

State and persistence: Uses per-task `current->utask`, thread PER fields, saved state in `struct arch_uprobe`, register state, and task flags. No persistent storage is kept beyond probe/task lifecycle.

Dependencies and integration: Depends on generic uprobes, die notifier chain from traps, s390 disassembler/probe opcode classification, ptrace/PER control registers, user access helpers, and return-probe stack semantics.

Risks and test signals: Highest risk is address fixup/emulation correctness for PC-relative instructions, PER event reproduction, and abort paths restoring PSW/int-code. Test signals include uprobes on loads/stores/branches, RIL instructions near range limits, 24/31-bit mode rejection, uretprobe return hijacking, ptrace PER single-step interactions, and fault injection for unaligned or inaccessible user operands.
