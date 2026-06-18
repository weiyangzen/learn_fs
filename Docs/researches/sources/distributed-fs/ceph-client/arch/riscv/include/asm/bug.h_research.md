<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h

## Purpose
Defines RISC-V BUG/WARN trap instruction encoding, bug-table entries, and trap-reporting interfaces.

## Important APIs, Types, And Functions
types `bug_entry`, `pt_regs`, `task_struct`; functions/prototypes `__show_regs`, `die`, `do_trap`; macros/constants `_ASM_RISCV_BUG_H`, `__INSN_LENGTH_MASK`, `__INSN_LENGTH_32`, `__COMPRESSED_INSN_MASK`, `__BUG_INSN_32`, `__BUG_INSN_16`, `GET_INSN_LENGTH(insn)`, `__BUG_ENTRY_ADDR`, `__BUG_ENTRY_FILE(file)`, `__BUG_ENTRY(file, line, flags)`, `ARCH_WARN_ASM(file, line, flags, size)`, `__BUG_FLAGS(cond_str, flags)`, `BUG()`, `__WARN_FLAGS(cond_str, flags) __BUG_FLAGS(cond_str, BUGFLAG_WARNING|(flags))`, plus 2 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `linux/const.h`, `linux/types.h`, `asm/asm.h`, `asm-generic/bug.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 99 lines, 2472 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h -->
