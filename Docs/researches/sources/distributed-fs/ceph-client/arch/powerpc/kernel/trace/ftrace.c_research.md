# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace.c

## Purpose
Implements the modern/common PowerPC dynamic ftrace text-patching backend for PPC32 and PPC64 mprofile/patchable-entry modes, including out-of-line stubs, call-ops, direct calls, module trampolines, init trampolines, and function graph tracing.

## Important APIs, Types, and Functions
- `ftrace_call_adjust()` maps compiler-recorded addresses to actual patch sites, including Clang PPC64 local-entry correction.
- `ftrace_read_inst()`, `ftrace_validate_inst()`, and `ftrace_modify_code()` safely verify and patch instructions.
- `ftrace_get_call_inst()` chooses direct branch, kernel ftrace trampoline, module trampoline, or fallback target.
- `ftrace_init_ool_stub()` allocates and patches an out-of-line stub when `CONFIG_PPC_FTRACE_OUT_OF_LINE`.
- `ftrace_replace_code()` overrides generic patching to update records in-place without stop_machine.
- `ftrace_init_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `arch_ftrace_update_code()`, `ftrace_dyn_arch_init()`, and `ftrace_free_init_tramp()` provide ftrace arch hooks.
- `ftrace_graph_func()` redirects return addresses for function graph tracing.

## Control Flow and State
Initialization builds text/init trampolines to `FTRACE_REGS_ADDR` or ftrace caller using TOC or PC-relative code. Each ftrace record is initialized by validating the compiler sequence, possibly patching mflr/std instructions, creating out-of-line stubs, and setting call-ops storage. Runtime updates iterate records, compute old/new ftrace targets, patch the call instruction or out-of-line stub, update call-ops pointers, and toggle original function patch sites for out-of-line mode.

## State and Persistence Behavior
Persists mutable instruction text at ftrace sites, trampoline areas, module trampolines/stubs, out-of-line stub reservations, and optional per-record ftrace ops pointers. `ftrace_tramps[]` tracks reachable kernel trampolines.

## Dependencies and Integration Points
Integrates with generic dynamic ftrace, modules, livepatch/direct calls through assembly entry code, PowerPC text patching/cache flush, TOC/PACATOC, section boundaries, compiler profiling sequences, and function graph tracer.

## Risks
Text patching must validate exact old instructions or it can corrupt arbitrary code. Branch-range limits require trampolines; missing reachable trampolines disables tracing. Compiler ABI changes, especially local/global entry behavior, can move patch sites. Out-of-line stubs must remain in branch range and their sequence must match `ftrace_entry.S` decoding.

## Test Signals
Enable/disable dynamic ftrace repeatedly, load/unload modules, run with Clang and GCC, patchable function entry, out-of-line stubs, call-ops, direct calls, livepatch, function graph tracer, inittext freeing, and records near branch range limits.
