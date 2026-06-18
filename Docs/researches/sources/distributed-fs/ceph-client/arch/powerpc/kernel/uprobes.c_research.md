# sources/distributed-fs/ceph-client/arch/powerpc/kernel/uprobes.c

## Purpose
Implements PowerPC architecture glue for user-space probes, including trap validation, out-of-line execution setup, single-step completion, exception notifier integration, and return-probe address hijacking.

## Important APIs, Types, And Functions
Defines `is_trap_insn`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `uprobe_get_swbp_addr`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_post_xol`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`, `arch_uprobe_skip_sstep`, `arch_uretprobe_hijack_return_addr`, and `arch_uretprobe_is_alive`. It uses `UPROBE_TRAP_NR` as a sentinel in `current->thread.trap_nr`.

## Control Flow
Probe analysis rejects unaligned addresses, prefixed instructions crossing a 64-byte boundary on ISA 3.1 CPUs, and instructions the architecture cannot single-step. Before XOL, it saves the task trap number, sets the sentinel, redirects NIP to the XOL slot, and enables user single-step. After single-step, it restores the saved trap number, sets NIP to the instruction following the probed instruction, and disables single-step. Die notifiers route breakpoint and single-step exceptions to generic uprobe pre/post handlers.

## State And Persistence
State lives in `current->utask->autask.saved_trap_nr`, `current->thread.trap_nr`, the saved user registers, and the temporary XOL mapping owned by generic uprobes. No durable persistence is involved.

## Dependencies And Integration Points
Depends on generic uprobes, die notifiers, PowerPC instruction helpers, software single-step and instruction emulation (`can_single_step`, `emulate_step`), and ptrace register helpers. Return probes integrate by replacing `regs->link` with a trampoline.

## Risks And Edge Cases
Prefixed instruction alignment is critical because placing a breakpoint in a split prefixed instruction would corrupt execution. XOL trap detection relies on every fault path changing `thread.trap_nr` away from the sentinel. Return-probe liveness depends on PowerPC stack direction and the chain-call special case.

## Test Signals
Run uprobes and uretprobes selftests on PowerPC, including branches/calls, emulated instructions, fatal XOL faults, single-step fallback, prefixed ISA 3.1 instructions near 64-byte boundaries, and nested return probes.
