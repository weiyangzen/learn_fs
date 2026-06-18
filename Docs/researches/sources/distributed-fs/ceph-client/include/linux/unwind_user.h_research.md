<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user.h -->
# sources/distributed-fs/ceph-client/include/linux/unwind_user.h

Purpose: declares the generic entry point and architecture hooks for unwinding user-space stack traces from kernel context.

Important APIs and types: includes `struct unwind_stacktrace` and state types from `unwind_user_types.h` plus architecture-specific definitions from `asm/unwind_user.h`. Fallback macros define no-op frame initialization when architecture frame-pointer support hooks are absent. `unwind_user_at_function_start()` defaults to false unless an architecture overrides it. `unwind_user()` fills stacktrace entries up to a maximum.

Control flow: tracing or diagnostic code prepares an `unwind_stacktrace`, then calls `unwind_user()`. Architecture code initializes user frame state and may identify function-entry IPs to improve unwinding semantics.

State and persistence: no state is owned here. It operates on caller-supplied stacktrace buffers and architecture-visible register/user stack state.

Dependencies and integration points: depends on generic unwind types and `asm/unwind_user.h`. It integrates with perf/tracing/deferred unwind code and architecture stack walking implementations.

Risks and test signals: risks include architecture hooks missing or inconsistent, user memory faults during stack walking, frame-pointer ABI assumptions, and truncated traces. Test per-architecture unwinding, invalid user stacks, signal/trampoline frames, max-entry limits, and builds without frame-pointer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/unwind_user.h -->
