# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.c

## Purpose
This formatter decodes `fspick` syscall flags for `perf trace`.

## Important APIs, Types, And Functions
It includes generated `fspick_arrays.c`, defines `strarray__fspick_flags`, and exposes `syscall_arg__scnprintf_fspick_flags()`.

## Control Flow
The formatter reads `arg->val` as an unsigned long and delegates directly to `strarray__scnprintf_flags()` with prefix behavior controlled by `arg->show_string_prefix`.

## State, Dependencies, And Integration
No persistent state is used. The generated table is produced by `fspick.sh`, and the formatter is declared in `beauty.h` as `SCA_FSPICK_FLAGS`.

## Risks And Test Signals
Correctness depends almost entirely on generated table freshness and flag bit indexing. Tests should cover known `FSPICK_*` flags, combinations, zero flags, and unknown bit fallback behavior.
