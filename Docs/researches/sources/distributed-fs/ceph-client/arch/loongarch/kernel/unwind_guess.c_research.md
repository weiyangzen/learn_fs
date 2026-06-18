# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_guess.c

Purpose: implements the LoongArch "guess" unwinder, exporting the standard unwinder interface while delegating frame traversal to `default_next_frame()`.

Important APIs, types, and functions: exports `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. It relies on `__unwind_start()`, `__unwind_get_return_address()`, `unwind_done()`, and `default_next_frame()`.

Control flow: `unwind_start()` initializes the state and, if the initial PC is not kernel text, immediately advances to the next guessed frame. `unwind_next_frame()` calls the stack-scanning fallback each time.

State and persistence: no persistent state. It mutates only `struct unwind_state` supplied by callers.

Dependencies and integration points: used when the kernel is configured for the guess unwinder or when prologue unwinding downgrades to `UNWINDER_GUESS`. Exported GPL symbols feed stacktrace users.

Risks: inherits all heuristic risks from `default_next_frame()` and lacks metadata validation. It can miss frames or include spurious frames when stack contents are ambiguous.

Test signals: boot-time stack dumps, WARN/OOPS traces, and forced stacktrace tests should produce bounded traces without invalid memory accesses.
