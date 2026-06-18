## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-ftrace.S` implements ARM64 ftrace entry
and function-graph tracing trampolines. It adapts compiler instrumentation call sites to generic
ftrace callbacks while preserving live AAPCS registers and constructing usable frame records for
stack unwinding.

### Important APIs, Types, And Functions
With `CONFIG_DYNAMIC_FTRACE_WITH_ARGS`, the central symbol is `ftrace_caller`, with optional direct
call paths `ftrace_caller_direct`, `ftrace_caller_direct_late`, and `ftrace_stub_direct_tramp`.
Without that mode, `_mcount`, `ftrace_caller`, and optional `ftrace_graph_caller` implement the
classic `-pg` path. Common stubs are `ftrace_stub`, `ftrace_stub_graph`, and
`return_to_handler()` for function graph returns. The code uses `struct ftrace_regs` offsets from
`asm-offsets.h`.

### Control Flow
In patchable-function-entry mode, enabled call sites branch to `ftrace_caller` after moving LR to
`x9`. The trampoline optionally loads per-callsite `ftrace_ops`, handles direct-call trampolines
without full register save when possible, saves argument registers and callsite metadata into
`ftrace_regs`, creates frame records, calls the selected tracer function, restores live registers,
and returns to the post-callsite PC or branches to a direct trampoline. In legacy mcount mode,
`_mcount` starts as a return-only stub, and patched call sites route through `ftrace_caller`, which
derives function PC/LR from frame records and invokes patched tracer or graph-tracer call sites.
`return_to_handler()` preserves return-value registers while asking generic graph tracing for the
original return address.

### State, Persistence, And Dependencies
The file stores no persistent state itself; ftrace core patches callsites and global labels such as
`ftrace_call` or `ftrace_graph_call`. Dependencies include dynamic ftrace, direct calls, function
graph tracer, compiler instrumentation mode, frame-pointer ABI, BTI landing pads, `ftrace_regs`
layout, and generic ftrace functions such as `prepare_ftrace_return()` and
`ftrace_return_to_handler()`.

### Integration Points
Generic ftrace patching code rewrites NOPs/branches that target these symbols. Kernel tracers,
function graph tracing, BPF/direct-call users, livepatch diagnostics, and perf-style function
tracing depend on this trampoline preserving the interrupted function ABI.

### Risks
Register preservation is subtle: x0-x8, FP, LR, PC, SP, and shadow call stack assumptions must match
the compiler and tracing ABI. Bad frame records break stack traces and graph tracing. Direct-call
paths must branch to valid BTI/PAC landing sites without unbalancing return prediction. Offset drift
between assembly and `struct ftrace_regs` silently corrupts tracing state.

### Test Signals
Dynamic ftrace enable/disable tests, function graph tracer tests, direct-call/BPF fentry tests,
stacktrace validation through traced functions, BTI/PAC builds, shadow-call-stack builds, legacy
`-pg` builds, and ftrace selftests under preemption/interrupt stress are important signals.
