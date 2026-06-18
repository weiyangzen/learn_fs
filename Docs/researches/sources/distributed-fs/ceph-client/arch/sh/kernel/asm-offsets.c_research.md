<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c

Purpose: generates assembly offsets for SH low-level code.

Important APIs/types/functions: `main()` emits `DEFINE()` constants for thread, task, pt_regs, sigframe, CPU context, and FPU/DSP offsets.

Control flow: build system compiles and runs this during offset generation; assembly includes the generated header.

State and persistence: no runtime state; it serializes C layout into assembly constants.

Dependencies/integration: must match `thread_info`, `task_struct`, `pt_regs`, signal, xstate, and CPU context layouts.

Risks: missing or stale offsets break exception entry, context switch, signal, and FPU save/restore.

Test signals: rebuild after struct changes and verify assembly compiles plus context-switch/signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/asm-offsets.c -->
