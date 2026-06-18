<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h

## Purpose
Defines SH hardware breakpoint state, UBC registration, perf breakpoint callbacks, and breakpoint-slot accounting.

## Important APIs, Types, And Functions
Includes `uapi/asm/hw_breakpoint.h`, `linux/kdebug.h`, `linux/types.h`. Key macros/constants include `__ASM_SH_HW_BREAKPOINT_H`, `__ARCH_HW_BREAKPOINT_H`, `HBP_NUM`, `hw_breakpoint_slots(type)`. Structures include `arch_hw_breakpoint`, `sh_ubc`, `clk`, `perf_event_attr`, `perf_event`, `task_struct`, `pmu`. Functions or extern declarations include `long`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_fill_perf_breakpoint`, `register_sh_ubc`, `perf_ops_bp`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `uapi/asm/hw_breakpoint.h`, `linux/kdebug.h`, `linux/types.h`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 72 lines, 2040 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/hw_breakpoint.h -->
