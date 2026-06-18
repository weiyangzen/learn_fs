<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c

Purpose: Implements RISC-V uprobes architecture hooks: breakpoint recognition, XOL preparation/restoration, single-step completion, return-probe liveness checks, exception notification, and instruction-cache maintenance for copied instruction slots.

Important APIs/types/functions: Provides `is_swbp_insn()`, `is_trap_insn()`, `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_skip_sstep()`, `arch_uprobe_abort_xol()`, `arch_uretprobe_is_alive()`, `arch_uprobe_exception_notify()`, `uprobe_breakpoint_handler()`, `uprobe_single_step_handler()`, and `arch_uprobe_copy_ixol()`.

Control flow: Analyze validates that the instruction can be probed, rejects unsupported compressed/illegal probe cases, stores the original opcode, and sets up the architecture slot. Pre-XOL redirects `epc` to the execute-out-of-line copy while saving the original PC; post-XOL adjusts `epc` back to the probed instruction stream unless a trap was recorded. Exception notifiers route breakpoint and single-step traps to the generic uprobes core.

State and persistence: Per-probe state lives in `struct arch_uprobe`; per-task transient state is stored in `current->utask`, including saved PC and trap number. No global persistent state is introduced.

Dependencies and integration points: Integrates Linux uprobes with RISC-V trap handling (`handle_break()`/single-step paths), `riscv_insn` decoding, copied instruction pages, and instruction-cache flushing.

Risks: Incorrect PC reconstruction after XOL can skip or re-execute user instructions. Return-probe stack checks must handle signal and syscall contexts without resurrecting dead return instances. Cache flush omissions can execute stale copied instructions.

Test signals: User-space uprobes on normal, compressed, branch, and trap instructions; return probes through nested calls; signal delivery during XOL; breakpoint and single-step exception paths; and instruction-cache coherency stress.

Source read size: 182 lines, 3780 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/uprobes.c -->
