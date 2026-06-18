<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h

## Purpose
Defines SH KGDB register sizing, trap numbers, breakpoint encoding, and register-set layout for remote debugging.

## Important APIs, Types, And Functions
Includes `asm/cacheflush.h`, `asm/ptrace.h`. Key macros/constants include `__ASM_SH_KGDB_H`, `_GP_REGS`, `_EXTRA_REGS`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `BREAK_INSTR_SIZE`, `BUFMAX`, `CACHE_FLUSH_IS_SAFE`, `GDB_ADJUSTS_BREAK_OFFSET`. Enums include `regnames`. Register or hardware-address constants include `_GP_REGS`, `_EXTRA_REGS`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `asm/cacheflush.h`, `asm/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_SMP`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 38 lines, 851 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kgdb.h -->
