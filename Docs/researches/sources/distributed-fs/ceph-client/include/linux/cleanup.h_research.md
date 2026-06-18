# sources/distributed-fs/ceph-client/include/linux/cleanup.h

## Purpose

`cleanup.h` implements scope-based cleanup, resource ownership transfer, and guard/lock helper macros using compiler cleanup attributes. It is intended to reduce goto-based unwind bugs and enforce LIFO cleanup ordering.

## Important APIs, Types, and Functions

Major macros are `DEFINE_FREE`, `__free`, `no_free_ptr`, `return_ptr`, `retain_and_null_ptr`, `DEFINE_CLASS`, `EXTEND_CLASS`, `CLASS`, `CLASS_INIT`, `scoped_class`, `DEFINE_GUARD`, `DEFINE_GUARD_COND`, `guard`, `ACQUIRE`, `ACQUIRE_ERR`, `scoped_guard`, `scoped_cond_guard`, `DEFINE_LOCK_GUARD_0/1`, `DEFINE_LOCK_GUARD_1_COND`, `DECLARE_LOCK_GUARD_*_ATTRS`, and `WITH_LOCK_GUARD_1_ATTRS`.

## Control Flow

Variables annotated with cleanup destructors run their cleanup at scope exit in reverse definition order. Guard macros acquire locks at declaration/construction and release them at cleanup. Scoped guard/class macros use a single-iteration `for` loop to bind lifetime to the following compound statement. Conditional guards skip or fail when acquisition does not succeed.

## State and Persistence Behavior

The macros create automatic variables, destructor wrappers, lock-class typedefs, and optional context-analysis aliases. They own no global state. Ownership transfer helpers null local variables so cleanup destructors do not free returned or consumed resources.

## Dependencies and Integration Points

It depends on compiler cleanup support, error-pointer helpers, argument-counting macros, and kernel type inference extensions. It integrates broadly with kernel resource-management patterns, locks, RCU/preempt guards, and static analysis annotations.

## Risks and Edge Cases

Definition order is semantic: resources acquired later are cleaned first. Mixing goto jumps with cleanup scopes can bypass intended structure and is discouraged. Top-of-function `__free(...)=NULL` can produce wrong lock/free order. Conditional guard error encoding must match `ACQUIRE_ERR()` expectations.

## Test Signals

Compile macro users under GCC and Clang, inspect generated cleanup ordering, test `return_ptr()` and `retain_and_null_ptr()` leak prevention, lockdep for guard scopes, conditional guard failure paths, and static analysis/context annotation behavior.
