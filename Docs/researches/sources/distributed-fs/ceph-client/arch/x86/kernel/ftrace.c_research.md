# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace.c

## Purpose
Provides x86 dynamic ftrace text patching, ftrace callback target updates, runtime trampoline allocation, and function graph return hook support.

## Important APIs, Types, And State
Implements `ftrace_arch_code_modify_prepare()`, `ftrace_arch_code_modify_post_process()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `ftrace_replace_code()`, `arch_ftrace_update_code()`, x86-64 trampoline functions (`arch_ftrace_update_trampoline()`, `arch_ftrace_trampoline_func()`, `arch_ftrace_trampoline_free()`), graph toggles, `prepare_ftrace_return()`, and optional `ftrace_graph_func()`. State includes `ftrace_poke_late`, dynamically allocated executable trampolines, and patched call/jump sites.

## Control Flow
Dynamic ftrace first verifies existing instruction bytes with `copy_from_kernel_nofault()`, then patches either directly during early/module load or through batched SMP text pokes under `text_mutex`. `ftrace_replace_code()` scans ftrace records, verifies all old call/nop encodings, then applies all new encodings and updates record state. Trampoline creation copies assembly caller stubs, appends a return thunk or ret, embeds an ops pointer, patches the callback call, and marks pages ROX. Function graph tracing patches `ftrace_graph_call` between a stub and graph caller, and return preparation replaces the saved return address with `return_to_handler` when graph entry succeeds.

## Dependencies And Integration Points
Depends on x86 text patching, execmem, ftrace core record iteration, module load paths, retpoline/rethunk choices, assembly labels in `ftrace_64.S`, and function graph tracer core.

## Risks And Test Signals
Risks include patching wrong bytes, racing module/livepatch text permission changes, broken trampoline layout if assembly labels move, W^X violations, and return-hook corruption. Tests should enable/disable dynamic ftrace, graph tracer, direct calls, regs callbacks, module tracing, livepatch coexistence, and inspect ftrace bug reports from verification failures.
