# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fadvise.sh

## Purpose
This generator emits an array mapping `POSIX_FADV_*` advice numbers to names for perf trace formatting.

## Important APIs, Types, And Functions
It reads `fadvise.h` from an optional or default UAPI linux header directory and emits `static const char *fadvise_advices[]`.

## Control Flow
The script greps decimal `POSIX_FADV_*` defines, rewrites each to `<number> <suffix>`, sorts numerically, formats array entries, and filters out s390-specific duplicate/odd `DONTNEED` and `NOREUSE` values at indexes 6 and 7.

## State, Dependencies, And Integration
The generated table is consumed by perf trace syscall argument formatters for fadvise-like syscalls. It depends on grep, sed, sort, xargs, and stable header formatting.

## Risks And Test Signals
The script contains a documented architecture hack and is not fully per-architecture. Cross-architecture perf.data formatting can be wrong for s390-like differences. Tests should verify common advice constants and document the known 6/7 filtering behavior.
