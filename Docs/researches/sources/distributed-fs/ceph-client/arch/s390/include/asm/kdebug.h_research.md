# sources/distributed-fs/ceph-client/arch/s390/include/asm/kdebug.h

Purpose: This header declares s390 debug die-notifier reason codes and the fatal `die()` entry point.

Important APIs/types/functions: `enum die_val` includes oops, breakpoint, single-step, panic, NMI, trap, GPF, call, and debug reasons; `die(struct pt_regs *, const char *)` is declared noreturn.

Control flow: Trap, probe, NMI, and fault handlers use the enum values when notifying debug infrastructure or terminating execution through `die()`.

State and persistence: No state is stored here; notifier chains and crash/oops state live elsewhere.

Dependencies and integration points: It integrates ptrace register context with oops handling, kprobes, kgdb-like debug paths, panic, and NMI handling.

Risks and test signals: Wrong reason codes reduce diagnostic quality or can confuse notifier consumers. Tests include breakpoint/single-step traps, oops reporting, panic paths, and debug-notifier consumers.
