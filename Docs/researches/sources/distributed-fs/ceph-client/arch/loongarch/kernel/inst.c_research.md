<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c

Purpose: implements LoongArch instruction simulation, safe text patching, and instruction generation helpers.
Important APIs and types: provides `simu_pc`, `simu_branch`, `insns_not_supported`, `insns_need_simulation`, `arch_simulate_insn`, `larch_insn_read`, `larch_insn_write`, `larch_insn_patch_text`, `larch_insn_text_copy`, and generators for NOP, branch, break, OR/move, LU12I/LU32I/LU52I, BEQ/BNE, and JIRL.
Control flow: emulation updates `pt_regs` PC/registers for PC-relative and branch instructions; patching validates alignment, writes with nofault copies under a raw spinlock, flushes icache, or uses `stop_machine_cpuslocked` after temporarily making pages writable and restoring ROX permissions.
State and persistence: text patching persistently modifies kernel/module code; simulation mutates transient exception register frames.
Dependencies and integration: used by kprobes/uprobes, ftrace, alternatives, jump labels, KGDB single-step, module patching, cache flush, and memory permission changes.
Risks and test signals: branch range errors, stale icache, or RWX restoration failures can crash the kernel. Signals include ftrace/kprobe/uprobe/jump-label selftests, module patching, strict RWX checks, and instruction emulator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/inst.c -->
