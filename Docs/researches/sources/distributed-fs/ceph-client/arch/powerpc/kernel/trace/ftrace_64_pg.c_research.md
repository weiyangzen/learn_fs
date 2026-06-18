# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg.c

## Purpose
Implements the older PPC64 profiling ABI dynamic ftrace backend used when not building with mprofile/patchable function entry. It patches `bl _mcount` call sites, handles TOC restore sequences, module trampolines, compiler long-branch trampolines, and function graph tracing.

## Important APIs, Types, and Functions
- `ftrace_call_adjust()` returns recorded addresses unchanged for this ABI.
- `ftrace_call_replace()`, `ftrace_modify_code()`, `test_24bit_addr()`, `is_bl_op()`, `is_b_op()`, and `find_bl_target()` build/validate branches.
- `setup_mcount_compiler_tramp()` rewrites compiler long-branch trampolines from `_mcount` to `ftrace_caller`/`ftrace_regs_caller`.
- `ftrace_make_nop()`, `ftrace_make_call()`, and `ftrace_modify_call()` patch direct, kernel trampoline, or module trampoline calls.
- `ftrace_update_ftrace_func()`, `ftrace_dyn_arch_init()`, and `ftrace_free_init_tramp()` manage global ftrace call target and kernel trampolines.
- Function graph helpers patch `ftrace_graph_call` and replace LR through `prepare_ftrace_return()`/`ftrace_graph_func()`.

## Control Flow and State
NOP conversion either patches a within-range branch to `nop`, rewrites kernel compiler trampolines then nops the call, or validates module trampoline target and patches a `b +8` over TOC restore. Call conversion validates the expected NOP/TOC sequence, selects a reachable trampoline, and patches a branch-link. Runtime callback updates patch `ftrace_call` and optionally `ftrace_regs_call`.

## State and Persistence Behavior
Mutates kernel/module text, compiler trampolines, and ftrace trampoline arrays. Module state includes `mod->arch.tramp` and `tramp_regs`.

## Dependencies and Integration Points
Depends on PPC64 ABI v1/v2 function entry rules, module trampoline target decoding, PowerPC text patching, dynamic ftrace core, function graph tracer, and assembly symbols in `ftrace_64_pg_entry.S`.

## Risks
The legacy ABI includes TOC restore hazards: a plain NOP can corrupt r2 if a task was preempted in a tracing call, hence the branch-over-load sequence. Wrong trampoline target validation or branch range handling can break modules or kernel text.

## Test Signals
PPC64 non-mprofile builds, dynamic ftrace toggles, module tracing, function graph tracing, regs and non-regs variants, long-branch trampolines, ABI v1 function descriptor cases, and TOC corruption stress.
