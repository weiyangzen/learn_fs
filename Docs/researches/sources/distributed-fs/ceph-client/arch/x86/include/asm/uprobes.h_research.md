# sources/distributed-fs/ceph-client/arch/x86/include/asm/uprobes.h

Purpose: x86 architecture definitions for user-space probes, including breakpoint instruction details and per-probe decoded instruction storage.

Important APIs/types/functions: `uprobe_opcode_t`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `ARCH_UPROBE_FLAG_CAN_OPTIMIZE`, `ARCH_UPROBE_FLAG_OPTIMIZE_FAIL`, `struct arch_uprobe`, `struct arch_uprobe_task`, and `is_uprobe_at_func_entry()`.

Control flow: uprobes patch user code with `int3` (`0xcc`), copy/decode original instructions into execute-out-of-line slots, and use per-instruction operation metadata for branches, default fixups, or push register fixups. Per-task state preserves trap number, TF, and on x86_64 a scratch register.

State/persistence: persistent probe state lives in `struct arch_uprobe`; per-thread execution state lives in `struct arch_uprobe_task`. The header defines layout, not storage ownership.

Dependencies/integration: depends on notifier infrastructure and `pt_regs`. Integrated with kernel uprobes, perf, tracing, and user unwinding function-entry detection.

Risks/test signals: instruction length, branch displacement, TF restoration, and optimized-probe flags are correctness-critical. Test uprobes on 32/64-bit processes, branches, pushes, optimized and non-optimized probes, single-step behavior, signal interaction, and unwind-at-function-entry behavior.
