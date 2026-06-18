# sources/distributed-fs/ceph-client/include/linux/typecheck.h

## Purpose
Provides compile-time type-checking macros that still evaluate as ordinary expressions in C code.

## Important APIs, Types, And Functions
Exports `typecheck(type, x)`, `typecheck_fn(type, function)`, and `typecheck_pointer(x)`.

## Control Flow
The macros rely on `typeof`, dummy variables, pointer comparison, assignment to a function-typed object, or dereferencing in `sizeof` to force compile-time diagnostics. `typecheck()` and `typecheck_pointer()` evaluate to `1`.

## State, Persistence, And Dependencies
No runtime state or external dependencies. All behavior is compile-time.

## Integration Points
Used by kernel macros that need to assert argument types while preserving expression usability, such as time/comparison/helper macros.

## Risks And Test Signals
Risks include GNU C dependency, side effects if arguments are not carefully handled by caller macros, and confusing diagnostics. Test signals are compile-fail tests for wrong scalar/function/pointer types and compile-pass use in conditional expressions.
