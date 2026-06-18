# sources/distributed-fs/ceph-client/kernel/static_call.c

## Purpose
`static_call.c` provides a tiny default static-call target, `__static_call_return0()`, that returns zero. It is used as a safe no-op/zero-return function for static call sites that need a valid callable target.

## Important APIs, types, and functions
- `long __static_call_return0(void)`: returns `0`.
- `EXPORT_SYMBOL_GPL(__static_call_return0)`: makes the helper available to GPL modules and core static call users.

## Control flow
There is no branching. Callers enter the helper and receive `0`.

## State and persistence behavior
No state is read or written.

## Dependencies and integration points
It includes `linux/static_call.h` and integrates with the static-call framework implemented by architecture code and `static_call_inline.c`.

## Risks
The helper is intentionally simple. The main risk is ABI/semantic mismatch if a static call site expects a non-`long` return or side effects; those sites must use correctly typed wrappers from the static-call macros.

## Test signals
Build/link coverage and static-call selftests are sufficient. Runtime signal is absence of unresolved `__static_call_return0` references when static calls or modules use a zero-return default.
