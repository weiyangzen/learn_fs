# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_orc.c

Purpose: implements the ORC unwinder for x86, using objtool-generated unwind tables to reconstruct call stacks without frame pointers.

Important APIs/functions: `unwind_init()`, `unwind_module_init()`, `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`. Important helpers include `orc_find()`, `__orc_find()`, module/ftrace/BPF lookup helpers, stack register dereference helpers, and ORC table sorting callbacks.

Control flow: boot-time `unwind_init()` validates ORC table sizes, builds a block lookup table for fast vmlinux text lookup, and enables the unwinder. Module init sorts module ORC IP/entry pairs. A live unwind starts from regs, current CPU registers, or an inactive task frame, validates stack membership, optionally skips the starting regs frame, and iteratively looks up ORC metadata for `ip - 1`. `unwind_next_frame()` calculates the previous stack pointer from the ORC SP rule, optionally dereferences indirect stack slots, recovers IP/SP from call or regs entries, restores BP according to ORC metadata, and prevents non-progressing stack loops.

State and persistence: boot-persistent state includes ORC table symbols, `orc_init`, `unwind_debug`, `lookup_num_blocks`, and module `arch.orc_*` pointers. Per-walk state lives in `struct unwind_state`, including regs/full-regs/partial-regs tracking and stack masks.

Dependencies and integration: tightly coupled to objtool output, `vmlinux.lds.S` ORC sections, module loader ORC data, dynamic ftrace trampolines, BPF JIT frame-pointer fallback, rethook/fgraph return recovery, RCU module lifetime protection, and x86 stack layouts.

Risks: corrupt or unsorted ORC tables disable or degrade unwinding. Missing ORC entries fall back to a guessed frame-pointer rule and mark the trace unreliable. Incorrect stack register rules can read wrong stack slots, loop, or lose interrupt/NMI frames.

Test signals: boot warnings for bad `.orc_unwind` tables, successful stack traces without frame pointers, module stack traces, ftrace trampoline traces, BPF JIT frames, NULL function pointer crashes, and debug dumps under `unwind_debug`.
