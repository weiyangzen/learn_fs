<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h

## Purpose
Defines SH low-level debug, unwind, trace, or linkage contracts for `ftrace` support.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_SH_FTRACE_H`, `MCOUNT_INSN_SIZE`, `FTRACE_SYSCALL_MAX`, `MCOUNT_ADDR`, `CALL_ADDR`, `STUB_ADDR`, `GRAPH_ADDR`, `CALLER_ADDR`, `MCOUNT_INSN_OFFSET`, `GRAPH_INSN_OFFSET`, `ftrace_return_address(n)`. Structures include `dyn_arch_ftrace`. Functions or extern declarations include `prepare_ftrace_return`, `mcount`, `return_address`, `arch_ftrace_nmi_enter`, `arch_ftrace_nmi_exit`. Register or hardware-address constants include `MCOUNT_ADDR`, `CALL_ADDR`, `STUB_ADDR`, `GRAPH_ADDR`, `CALLER_ADDR`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_FUNCTION_TRACER`, `CONFIG_DYNAMIC_FTRACE`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 58 lines, 1444 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/ftrace.h -->
