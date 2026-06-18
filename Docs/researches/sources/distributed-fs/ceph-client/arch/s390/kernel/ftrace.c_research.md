# sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.c

## Purpose
Implements the s390 dynamic ftrace backend. It patches compiler-generated function-entry instructions, manages hotpatch trampolines on machines without sequential-instruction support, updates the active ftrace function, supports graph tracing, and integrates kprobes-on-ftrace.

## Important APIs, Types, And Functions
Important functions include `ftrace_need_init_nop()`, `ftrace_init_nop()`, `ftrace_modify_call()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `arch_ftrace_update_code()`, `ftrace_arch_code_modify_post_process()`, optional `ftrace_graph_func()`, `kprobe_ftrace_handler()`, and `arch_prepare_kprobe_ftrace()`. State includes global `ftrace_func` and hotpatch trampoline ranges from `ftrace.h`.

## Control Flow
For CPUs with sequential instruction support, calls/nops are patched by replacing a six-byte branch instruction at the recorded function IP. Without it, `ftrace_init_nop()` allocates a per-site trampoline, writes a shared trampoline branch and target metadata, then changes only the branch displacement or mask. Code modification verifies expected old bytes before patching and synchronizes instruction fetch after updates. Graph tracing rewrites the saved return address to `return_to_handler`. Kprobe ftrace handler emulates probe pre/post handlers using ftrace regs.

## State And Persistence
Patches live kernel/module text and trampoline slots. `ftrace_func` is read-mostly global state. Module architecture data tracks trampoline allocation.

## Dependencies And Integration Points
Depends on ftrace core, module metadata, text patching, cache synchronization, nospec expoline state, kprobes, KMSAN unpoisoning, and generated ftrace register offsets.

## Risks And Edge Cases
Instruction alignment, expected-byte verification, displacement range, trampoline exhaustion, module lifetime, expoline selection, and concurrent text patching are all sensitive. Wrong return-address handling breaks graph tracing.

## Test Signals
Signals include ftrace selftests, function graph tracer tests, kprobes-on-ftrace tests, module tracing, CPUs with and without seq-insn support, expoline toggles, and text patch failure injection.
