# sources/distributed-fs/ceph-client/arch/arm64/kernel/return_address.c

Purpose: this file implements the generic `return_address()` helper for ARM64 using the architecture stack unwinder.

Important APIs and state: `struct return_address_data` carries a target frame level and output address. `save_return_addr()` is the stack-walk callback and is marked `NOKPROBE_SYMBOL`. `return_address()` is exported GPL and also marked not probeable.

Control flow: `return_address(level)` adds 2 to the requested level to skip its own frames, initializes the result to NULL, and calls `arch_stack_walk()` over the current task. The callback decrements the level for each PC; when the target level is reached, it stores the PC and stops the walk. If the walk ended before the requested level, NULL is returned.

Dependencies and integration: depends on ARM64 stacktrace unwinding and ftrace users that call `return_address()`. The NOKPROBE annotations prevent recursive instrumentation of unwinder-sensitive code.

Risks: returned PCs depend on frame-pointer/unwind reliability, compiler instrumentation, and skipped frame count. It should not be used as a security boundary. Probing it would risk recursion through stack walking.

Test signals: ftrace users, stacktrace tests, and callers expecting NULL for excessive levels. Bad behavior appears as incorrect caller addresses or unwinder recursion.
