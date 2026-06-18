<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h

## Purpose
Defines SH kprobe instruction slots, decoded-instruction metadata, breakpoint/restore opcodes, and arch kprobe hooks.

## Important APIs, Types, And Functions
Includes `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`. Key macros/constants include `__ASM_SH_KPROBES_H`, `BREAKPOINT_INSTRUCTION`, `MAX_INSN_SIZE`, `MAX_STACK_SIZE`, `MIN_STACK_SIZE(ADDR)`, `flush_insn_slot(p)`, `kretprobe_blacklist_size`, `kprobe_handle_illslot(pc)`. Structures include `kprobe`, `arch_specific_insn`, `prev_kprobe`, `kprobe_ctlblk`. Typedefs include `kprobe_opcode_t`. Functions or extern declarations include `arch_remove_kprobe`, `__kretprobe_trampoline`, `kprobe_fault_handler`, `kprobe_handle_illslot`. Register or hardware-address constants include `MIN_STACK_SIZE(ADDR)`.

## Control Flow
Runtime flow is callback-driven through tracing, probe, debug, unwind, or exception paths. The definitions describe register state, patched instructions, breakpoint slots, CFI records, and entry points used by implementation files.

## State And Persistence
State lives in patched text, unwind tables, exception tables, debug registers, kprobe/ftrace records, stack frames, and trap frames. The header defines layout and declarations for those externally managed records.

## Dependencies And Integration Points
It directly depends on `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`. Kconfig-sensitive paths mention `CONFIG_KPROBES`. Integration points are ftrace, perf, kprobes, KGDB, unwinder, exception tables, stacktrace, and trap notification code.

## Risks And Edge Cases
Risks include corrupting patched instruction streams, mismatched breakpoint lengths, incomplete unwind metadata, lost trap-frame state, and debug/probe callbacks diverging from entry assembly.

## Test Signals
Useful signals are ftrace/function-graph tests, kprobe/KGDB smoke tests, perf breakpoint tests, oops/BUG decoding, stacktrace/unwind checks, and exception-table fault-injection tests.

Source read size: 55 lines, 1302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kprobes.h -->
