# sources/distributed-fs/ceph-client/arch/xtensa/kernel/stacktrace.c

Purpose: Walks Xtensa kernel and user call stacks for perf, diagnostics, generic stacktrace, and `return_address()`.

Important APIs, types, and functions: `xtensa_backtrace_user()`, `xtensa_backtrace_kernel()`, `walk_stackframe()`, `save_stack_trace_tsk()`, `save_stack_trace()`, `return_address()`, `struct stackframe`, and callbacks for stack trace collection.

Control flow: User backtrace first emits current PC/SP, walks valid register windows using `windowstart/windowbase`, then follows spilled stack frames with guarded `__get_user()` reads. Kernel backtrace spills registers, walks stack frames inside the thread stack, recognizes `common_exception_return` to transition into user unwinding, and uses callbacks for each frame. Generic `walk_stackframe()` follows saved `a0/a1` pairs until stack progress stops.

State and persistence: Mostly read-only, but `spill_registers()` writes live register windows to the current stack. Stack trace APIs fill caller-provided buffers and return-address state.

Dependencies and integration: Depends on Xtensa window ABI conventions, `MAKE_PC_FROM_RA`, `SPILL_SLOT`, `kernel_text_address`, `common_exception_return`, user access helpers, perf events, and generic `CONFIG_STACKTRACE` interfaces.

Risks: Bad or corrupted `a1` chains terminate early or can skip frames; user unwinding is unavailable for call0-only/probed non-windowed state; stack walking assumes monotonic SP progress; exception-frame detection is tightly coupled to vector return code.

Test signals: Validate perf callchains, `dump_stack`, `/proc` stack users, kernel oops traces, call0 vs windowed userspace, user-stack fault handling, and traces through exception return.
