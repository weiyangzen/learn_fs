# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind.c

Purpose: provides the generic fallback stack-scanning unwinder used by LoongArch unwinder implementations when no stronger metadata is available.

Important APIs, types, and functions: `default_next_frame(struct unwind_state *state)` scans `state->stack_info` for kernel-text return addresses. It uses `unwind_done()`, `get_stack_info()`, `unwind_graph_addr()`, and `__kernel_text_address()`.

Control flow: starting one word above the current stack pointer, it walks each stack segment until `info->end`, treats each word as a possible return address, translates function-graph tracer return addresses, and accepts the first kernel text address as the next PC. If the segment ends, it jumps to `info->next_sp` and asks `get_stack_info()` for the next stack segment.

State and persistence: mutates only the passed `unwind_state` by advancing `sp`, updating `pc`, and consuming stack segment metadata. It has no global state.

Dependencies and integration points: called by `unwind_guess.c` directly and by `unwind_prologue.c` when prologue analysis cannot operate. It is part of stacktrace, dump, warning, and live debugging paths.

Risks: this is heuristic and can report false positives from stack data that looks like a kernel address. It should be treated as less reliable than ORC or prologue unwinding.

Test signals: stacktrace output under deep call chains, IRQ stacks, and function graph tracing should continue to make progress without crossing invalid stack bounds.
