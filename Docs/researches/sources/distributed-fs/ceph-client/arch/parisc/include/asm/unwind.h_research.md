<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h

Source read size: 85 lines, 2723 bytes.

Purpose: defines PA-RISC unwind table metadata and stack-walking interfaces. Important APIs/types: `MAX_UNWIND_ENTRIES`, `struct unwind_table_entry` with ABI bitfields, `struct unwind_table`, `struct unwind_frame_info`, and functions `unwind_frame_init()`, `unwind_frame_init_from_blocked_task()`, `unwind_once()`, `unwind_to_user()`, and `unwind_init()`. Control flow: unwind code uses ABI table entries to determine saved registers, frame size, and continuation state while walking kernel or blocked-task stacks. State and persistence: unwind tables are linked on a list and persist for core kernel/modules; frame info is per-walk transient. Dependencies and integration points: consumed by `kernel/unwind.c`, stacktrace, oops reporting, ftrace, and module unwind registration. Risks: C bitfield layout must match PA-RISC unwind ABI; bad region bounds or frame rules produce broken stack traces or unsafe unwinds. Test signals: stacktrace selftests, oops/backtrace output, module load/unload unwind coverage, blocked-task traces, and ftrace/function-graph tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/unwind.h -->
