# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/fpu.h

Purpose: defines x86 FPU tracepoints for observing FPU save/load/register activation and xstate validation events.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(x86_fpu)` and events `x86_fpu_before_save`, `x86_fpu_after_save`, `x86_fpu_regs_activated`, `x86_fpu_regs_deactivated`, `x86_fpu_dropped`, `x86_fpu_copy_dst`, and `x86_fpu_xstate_check_failed`.

Control flow: each event accepts `struct fpu *`, records the current `TIF_NEED_FPU_LOAD` state, and, when `X86_FEATURE_OSXSAVE` is available, reads `xfeatures` and `xcomp_bv` from the task fpstate xsave header. The trace include macros route generated code through `trace/define_trace.h`.

State/persistence: no persistent state is owned here. The trace payload snapshots FPU pointer, lazy-load flag, and xsave header fields at event emission time.

Dependencies/integration: depends on Linux tracepoint infrastructure, thread flags, CPU feature checks, and FPU/xstate internals. Integrated by FPU management code around save/restore and error paths.

Risks/test signals: instrumentation must not dereference xsave fields unless OSXSAVE exists. Trace output should be checked with ftrace/perf while exercising FPU-heavy workloads, fork/exec, signal delivery, lazy FPU load, and xstate corruption/error handling paths.
