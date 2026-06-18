<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/user.c -->
# sources/distributed-fs/ceph-client/kernel/unwind/user.c

Purpose: implements generic user-space stack unwinding, currently centered on frame-pointer based unwinding when architecture support is present.

Important APIs: `unwind_user()` fills `struct unwind_stacktrace` with instruction pointers. Internal helpers include `unwind_user_start()`, `unwind_user_next()`, `unwind_user_next_fp()`, `unwind_user_next_common()`, and `get_user_word()`.

Control flow: start validates that current is not a kernel thread and that registers are in user mode, initializes IP, SP, FP, word size, and available unwind methods. The loop records the current IP, then advances using the selected method. Frame-pointer unwinding calculates CFA, validates stack growth, alignment, and user memory reads, loads return address and optional next frame pointer, and updates state. Failure marks the unwind done.

State and persistence: no global state is stored. The unwind state is stack-local, and output is caller-owned.

Dependencies and integration: depends on architecture macros such as `ARCH_INIT_USER_FP_FRAME`, `unwind_user_at_function_start()`, `unwind_user_word_size()`, register helpers, and `get_user()`. It is used directly and by deferred unwind.

Risks: user stacks are untrusted, so every frame transition must validate monotonic stack progress and alignment. Compat word-size handling matters on mixed 32/64-bit systems. Test signals include invalid user pointers, zero max entries, kernel threads, function-entry top frame handling, compat word size, and frame chains with malformed CFA/FP values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/unwind/user.c -->
