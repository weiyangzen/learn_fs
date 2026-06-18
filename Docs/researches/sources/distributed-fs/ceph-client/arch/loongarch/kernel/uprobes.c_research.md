# sources/distributed-fs/ceph-client/arch/loongarch/kernel/uprobes.c

Purpose: provides LoongArch architecture hooks for uprobes and uretprobes, including instruction validation, execute-out-of-line setup, simulation, and return address hijacking.

Important APIs, types, and functions: implements `arch_uprobe_analyze_insn()`, `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, `arch_uprobe_skip_sstep()`, `arch_uretprobe_hijack_return_addr()`, `arch_uretprobe_is_alive()`, `uprobe_breakpoint_handler()`, `uprobe_singlestep_handler()`, `uprobe_get_swbp_addr()`, and `arch_uprobe_copy_ixol()`.

Control flow: instruction analysis rejects unaligned probe addresses and unsupported instructions. Instructions needing simulation install a NOP into the XOL slot and set `simulate`; otherwise the original instruction is copied followed by the XOL breakpoint. Pre-XOL saves `trap_nr`, tags the task with `UPROBE_TRAP_NR`, and redirects PC to the XOL slot. Post-XOL restores trap state and advances PC by one instruction; abort restores the original probe address. Simulated instructions are interpreted by `arch_simulate_insn()`.

State and persistence: per-task uprobe state lives in `current->utask` and `current->thread.trap_nr`. Uretprobes replace GPR1/RA with the trampoline and compare saved stack values for liveness.

Dependencies and integration points: depends on generic uprobes, LoongArch instruction analysis/simulation, cache flushing, highmem page mapping, and ptrace PC helpers.

Risks: instruction classification is critical because non-simulatable PC-relative or control-flow instructions cannot safely execute out of line. Cache flushing must cover copied XOL bytes. Return-probe liveness depends on LoongArch stack direction and SP conventions.

Test signals: kernel uprobe selftests, perf probe on LoongArch user binaries, uretprobe nested calls, unsupported instruction rejection, and XOL cache-coherency tests.
