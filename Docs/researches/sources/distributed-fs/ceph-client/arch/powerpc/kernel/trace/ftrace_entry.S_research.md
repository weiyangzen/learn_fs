# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_entry.S

## Purpose
Provides the common PowerPC ftrace assembly entry points for modern dynamic ftrace, including regs/non-regs callers, direct calls, out-of-line stubs, livepatch redirection, `_mcount`, function graph return handling, and reserved out-of-line/trampoline storage.

## Important APIs, Types, and Functions
- `ftrace_regs_entry`/`ftrace_regs_exit` macros build and tear down synthetic stack frames and `pt_regs`.
- `ftrace_regs_caller` saves all registers for regs-capable tracing; `ftrace_caller` saves the minimal set.
- `ftrace_call` and `ftrace_regs_call` are patch sites for the C callback.
- Direct-call labels bypass normal ftrace when `FTRACE_OPS_DIRECT_CALL` is present.
- `livepatch_handler` redirects execution to patched replacement functions while preserving a livepatch stack.
- `_mcount`/`mcount` are exported when patchable function entry is not used.
- `return_to_handler` calls `ftrace_return_to_handler` for function graph tracing.
- `ftrace_ool_stub_text` reserves out-of-line stub slots.

## Control Flow and State
Entry creates a minimal frame for the traced callee plus a switch frame containing `pt_regs`, extracts the call-site IP from LR or out-of-line stub decoding, saves parent LR, loads ftrace ops/callback, calls it, then restores registers and returns past the call site. Exit can route to direct-call target, livepatch handler, out-of-line return, or normal branch-through-CTR.

## State and Persistence Behavior
Uses per-call stack frames, optional livepatch per-thread stack pointer, PACA TOC/ftrace enable flag, and mutable NIP/LR in `pt_regs`. Reserved out-of-line stub text is patched by `ftrace.c`.

## Dependencies and Integration Points
Coupled to `ftrace.c` instruction sequence assumptions, `asm-offsets.h`, livepatch thread-info fields, `function_trace_op`, dynamic ftrace call-ops/direct-call layouts, ftrace graph infrastructure, and PPC32/PPC64 ABI differences.

## Risks
This code runs between function prologue stages, so stack/LR/TOC assumptions are narrow. Out-of-line decoding must match stub layout. Livepatch handler cannot allocate a normal frame and must preserve only allowed volatile state. Direct-call and graph paths must not corrupt return values.

## Test Signals
Dynamic ftrace with regs/non-regs, direct calls, call-ops, out-of-line stubs, livepatch transitions, function graph tracer, PPC32 and PPC64 builds, modules, and stack unwinder reliability while tracing.
