<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once_lite.h -->
# sources/distributed-fs/ceph-client/include/linux/once_lite.h

## Purpose
This header provides a lightweight call-once macro family that does not use jump-label patching.

## Important APIs, types, and functions
`DO_ONCE_LITE()` unconditionally performs once-guarded function execution. `DO_ONCE_LITE_IF()` runs the function once only when a condition is true. `__ONCE_LITE_IF()` implements the static boolean guard in `.data..once`.

## Control flow
The condition is evaluated into a local boolean. If true and the per-callsite static flag is not set, the flag is set and the function is invoked. The macro returns whether the input condition was true, not whether the function actually ran.

## State and persistence
State is a per-expansion static `bool __already_done` that persists for kernel/module lifetime. There is no static-key patching and no explicit locking.

## Dependencies and integration points
It depends on basic types and likely/unlikely/compiler section support inherited from broader kernel headers. It is useful in low-overhead paths where jump-label infrastructure is not desired.

## Risks and test signals
Risks include races because the guard is not atomic, misunderstanding the return value, separate state per macro expansion, and side-effect arguments only executing once. Test concurrent calls if used in shared paths, conditional false-then-true behavior, and build coverage for section placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once_lite.h -->
