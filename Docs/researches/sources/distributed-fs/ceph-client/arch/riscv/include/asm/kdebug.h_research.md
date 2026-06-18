<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h

## Purpose
Defines die-notifier event values for RISC-V debug/oops paths.

## Important APIs, Types, And Functions
types `die_val`; macros/constants `_ASM_ARC_KDEBUG_H`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 12 lines, 158 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h -->
