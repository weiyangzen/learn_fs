<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h

## Purpose
Declares RISC-V relative exception-table format and fixup handlers.

## Important APIs, Types, And Functions
types `exception_table_entry`, `pt_regs`; functions/prototypes `fixup_exception`, `ex_handler_bpf`; macros/constants `_ASM_RISCV_EXTABLE_H`, `ARCH_HAS_RELATIVE_EXTABLE`, `swap_ex_entry_fixup(a, b, tmp, delta)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 52 lines, 1495 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h -->
