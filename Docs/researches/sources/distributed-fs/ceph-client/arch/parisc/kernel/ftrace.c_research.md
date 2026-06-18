# sources/distributed-fs/ceph-client/arch/parisc/kernel/ftrace.c

## Purpose

`ftrace.c` implements PA-RISC function tracing support. It provides the runtime trampoline invoked from compiler-generated patchable call sites, dynamic ftrace patching, optional function-graph return hooking, and the kprobes-on-ftrace bridge.

## Important APIs, Types, And Functions

`ftrace_func` stores the active trace callback installed by `ftrace_update_ftrace_func()`. `ftrace_function_trampoline()` calls the current function tracer with `self_addr`, `parent`, `function_trace_op`, and ftrace register state.

When `CONFIG_FUNCTION_GRAPH_TRACER` is enabled, `ftrace_graph_enable` is a static key toggled by `ftrace_enable_ftrace_graph_caller()` and `ftrace_disable_ftrace_graph_caller()`. `prepare_ftrace_return()` replaces the saved return pointer with `parisc_return_to_handler` after `function_graph_enter()` accepts the edge.

Dynamic ftrace entry points include `ftrace_call_adjust()`, `ftrace_make_call()`, and `ftrace_make_nop()`. The make-call path builds PA-RISC instruction templates, checks that the patch region is still all NOPs using `copy_from_kernel_nofault()`, and patches text with `__patch_text_multiple()`. On 64-bit, it handles an unaligned callsite variant and dereferences function descriptors before embedding the target address.

With `CONFIG_KPROBES_ON_FTRACE`, `kprobe_ftrace_handler()` maps ftrace hits into kprobe pre/post handling, and `arch_prepare_kprobe_ftrace()` marks the optimized kprobe instruction slot as unused.

## Control Flow

At runtime a patched callsite branches into a trampoline sequence that reaches `ftrace_function_trampoline()`. The trampoline invokes the active ftrace callback first. If graph tracing is enabled, it locates the caller return pointer on the stack using the original stack pointer and `RP_OFFSET`; it only modifies the return slot if the saved value matches `parent`.

For dynamic enablement, ftrace computes the adjusted callsite address as the last instruction in the patchable function area. `ftrace_make_call()` chooses a 32-bit or 64-bit trampoline template, verifies the reserved instructions are NOPs, and writes the trampoline. `ftrace_make_nop()` restores the callsite and preceding reserved instructions to `INSN_NOP`.

The kprobe bridge prevents recursion with `ftrace_test_recursion_trylock()`, looks up a kprobe at `ip`, sets per-CPU current kprobe state, runs pre handlers, advances `iaoq`, optionally runs post handlers, and clears state before unlocking recursion.

## State And Persistence Behavior

State is runtime-only: patched kernel text, `ftrace_func`, the graph static key, and per-CPU kprobe state. No persistent storage is used. Text patches persist until ftrace or kprobe infrastructure reverses them.

## Dependencies And Integration Points

The file depends on the generic ftrace, function graph, kprobes, jump label, user nofault copy, PA-RISC assembly offsets, function descriptors, and text patching APIs. It integrates with compiler-generated patchable function entries and the architecture's return-pointer stack frame layout.

## Risks

Instruction template size and placement are critical; an incorrect `FTRACE_PATCHABLE_FUNCTION_SIZE`, unaligned 64-bit case, or wrong descriptor dereference can corrupt executable text. The return-hook sanity check prevents some stack corruption, but it depends on `org_sp_gr3` and `RP_OFFSET` matching entry assembly. Kprobe-on-ftrace must preserve `iaoq` ordering and avoid recursion leaks.

## Test Signals

Signals include enabling and disabling function tracing through tracefs, running function graph tracing, loading modules with ftrace callsites, verifying no `-EINVAL` from non-NOP patch regions, using kprobes optimized through ftrace, and checking that trace callbacks receive correct parent/self addresses on both 32-bit and 64-bit kernels.
