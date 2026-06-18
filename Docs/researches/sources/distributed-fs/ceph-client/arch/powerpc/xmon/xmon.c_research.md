<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c

## Purpose
Implements the PowerPC xmon in-kernel monitor: exception entry, SMP rendezvous, command interpreter, breakpoints, memory inspection and mutation, register dumps, stack walking, symbol lookup, platform diagnostics, sysrq/debugfs control, and early boot enablement.

## Important APIs, Types, And Functions
Important entry points are `xmon()`, `xmon_irq()`, `xmon_setup()`, `early_parse_xmon()`, and debugger hooks registered by `xmon_init()`. Core helpers include `xmon_core()`, `cmds()`, `bpt_cmds()`, `mread()`, `mwrite()`, `mread_instr()`, `read_spr()`, `write_spr()`, `do_step()`, `xmon_show_stack()`, `show_pte()`, `dump_log_buf()`, and `clear_all_bpt()`. State is represented by `struct bpt`, `bpts[]`, `dabr[]`, `iabr`, `in_xmon`, `xmon_on`, `xmon_is_ro`, and SMP masks/ownership fields.

## Control Flow
Exception or sysrq entry disables interrupts, checks lockdown, removes CPU breakpoints, coordinates other CPUs into xmon on SMP, prints exception context, and runs the command loop on the owning CPU. Commands dispatch to memory, dump, breakpoint, register, CPU-switch, trace, task, reboot, procedure-call, and symbol handlers. Exit reinserts breakpoints, releases other CPUs, restores watchdog/tracing state, and returns whether execution may continue.

## State And Persistence
Persistent monitor state includes enabled software breakpoints, data breakpoints, instruction breakpoint selection, default dump/memory sizes, last command repetition, read-only mode, and debugfs/sysrq enablement. Runtime state includes temporary bus-error and SPR-fault longjmp buffers, current input line, and the set of CPUs stopped in xmon.

## Dependencies And Integration Points
Integrated with PowerPC debugger hook globals, text patching, hw breakpoint APIs, kallsyms, kmsg dump, ftrace, debugfs, sysrq, RTAS surveillance, OPAL/XIVE diagnostics, paca/MMU structures, watchdogs, security lockdown, SMP IPIs, and the nonstdio console backend.

## Risks And Edge Cases
This is privileged live-kernel debugging code. Risks include corrupting memory or SPRs, failing to restore patched instructions, placing breakpoints on prefixed-instruction suffixes, deadlocking during SMP rendezvous, stale stack/PACA reads, and lockdown bypass if read-only checks regress. Recovery relies on careful fault catching around direct memory and SPR access.

## Test Signals
Signals are successful kernel entry through sysrq or `xmon=early`, safe return from faults inside memory/SPR reads, breakpoint hit/clear/reinsert behavior, single-step behavior, SMP CPU switching, read-only mode refusing writes/procedure calls/breakpoints, and command output for registers, stack, logs, PTEs, tasks, and platform diagnostics.

Source read size: 4092 lines, 88178 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/xmon.c -->
