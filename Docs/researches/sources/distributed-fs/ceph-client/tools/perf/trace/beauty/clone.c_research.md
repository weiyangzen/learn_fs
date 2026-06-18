# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.c

## Purpose
This formatter decodes `clone`/related clone flag bitmasks for `perf trace` and masks syscall arguments that are irrelevant unless specific clone flags are present.

## Important APIs, Types, And Functions
The local helper `clone__scnprintf_flags()` includes generated `clone_flags_array.c`, defines `strarray__clone_flags`, and calls `strarray__scnprintf_flags()`. Public formatter `syscall_arg__scnprintf_clone_flags()` uses `CLONE_PARENT_SETTID`, `CLONE_CHILD_SETTID`, `CLONE_CHILD_CLEARTID`, and `CLONE_SETTLS`.

## Control Flow
The formatter reads `flags = arg->val`, conditionally sets bits in `arg->mask` for parent tid pointer, child tid pointer, and TLS arguments when the corresponding clone flags are absent, then returns the rendered flag string.

## State, Dependencies, And Integration
Static generated data maps flag bit positions to names. Runtime state mutation is limited to `arg->mask`, which affects later argument display in `perf trace`. The formatter is exposed as `SCA_CLONE_FLAGS` through `beauty.h`.

## Risks And Test Signals
Correctness depends on generated flag tables and mask bit positions matching syscall argument indexes. Tests should verify flags render with and without `CLONE_` prefixes and that unused pointer arguments are hidden when controlling flags are absent.
