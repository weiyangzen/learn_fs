# File Research: sources/cow-pools/bcachefs-tools/include/linux/cleanup.h

This header ports Linux scope-based cleanup helpers into bcachefs-tools. It defines `DEFINE_FREE()`, `__free()`, `no_free_ptr()`, and `return_ptr()` for compiler cleanup-attribute ownership transfer, plus class/guard helpers for RAII-style resource management.

The main abstractions are `DEFINE_CLASS()`, `EXTEND_CLASS()`, `CLASS()`, `DEFINE_GUARD()`, `DEFINE_GUARD_COND()`, `guard()`, `scoped_guard()`, and `scoped_cond_guard()`. These wrap cleanup destructors around automatic variables and enforce LIFO cleanup order. The documentation is unusually important: it warns that declaration order matters for dependent resources such as lock-held allocations, and that cleanup helpers should not be mixed with `goto` unwinds in the same routine.

It also provides `DEFINE_LOCK_GUARD_0/1()` and conditional variants for guard types that need explicit lock state or stored metadata. Other headers in this group use it to define mutex, percpu rwsem, irq, preempt, and RCU guards.
