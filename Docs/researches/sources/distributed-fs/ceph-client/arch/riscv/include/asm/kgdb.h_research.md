<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h

## Purpose
Defines KGDB register numbering, packet sizes, breakpoint instruction size, and breakpoint helper.

## Important APIs, Types, And Functions
functions/prototypes `arch_kgdb_breakpoint`, `kgdb_compiled_break`; macros/constants `__ASM_KGDB_H_`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `BREAK_INSTR_SIZE`, `DBG_REG_ZERO`, `DBG_REG_RA`, `DBG_REG_SP`, `DBG_REG_GP`, `DBG_REG_TP`, `DBG_REG_T0`, `DBG_REG_T1`, plus 66 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/build_bug.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 111 lines, 2701 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h -->
