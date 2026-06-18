# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdebug.h

Purpose: Defines PowerPC debug/trap notification values for die-chain users and low-level exception diagnostics.

Important APIs, types, and functions: Provides architecture-specific `DIE_*` event constants used by notifier callbacks around oops, breakpoint, single-step, and other trap conditions.

Control flow: Exception code raises die notifications with these event IDs; registered kernel debuggers, kprobes, and diagnostics decide whether to handle or pass through.

State and persistence: No state in the header. Notification state is in generic notifier chains.

Dependencies and integration points: Integrates with `die()`/notifier, kprobes, kgdb, xmon, and exception handling.

Risks: Event ID compatibility matters for notifier users. Mislabeling trap types can cause a debugger/probe to consume the wrong exception.

Test signals: Breakpoint, single-step, oops, kprobe, and kgdb notifier paths; verify notifier return behavior and event IDs.
