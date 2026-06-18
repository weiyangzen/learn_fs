# sources/distributed-fs/ceph-client/tools/perf/perf.h

### Purpose
`perf.h` is a small shared perf header defining global constants and affinity mode identifiers used by perf internals.

### Important APIs, Types, And Functions
It defines `MAX_NR_CPUS` as 4096 and `enum perf_affinity` values `PERF_AFFINITY_SYS`, `PERF_AFFINITY_NODE`, `PERF_AFFINITY_CPU`, and `PERF_AFFINITY_MAX`.

### Control Flow
No runtime control flow exists.

### State And Persistence
No state is defined.

### Dependencies And Integration Points
It is included by `perf.c` and other perf code needing common CPU/affinity definitions.

### Risks
`MAX_NR_CPUS` is a fixed compile-time limit that can be too low for very large systems if used for static arrays. Enum values are API-like within perf and should stay stable for users of the type.

### Test Signals
Build coverage plus runtime tests on large CPU-count systems or code paths that select system/node/CPU affinity modes.
