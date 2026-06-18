# Research: sources/distributed-fs/ceph-client/tools/perf/bench/bench.h

Purpose: central declaration header for `perf bench` benchmark entry points, shared timing globals, output formats, and portability shims.

Important APIs/types/functions: declares `bench__start`, `bench__end`, `bench__runtime`, all `bench_*` command functions, `bench_format`, `bench_repeat`, and format constants. It also defines missing `MADV_HUGEPAGE`/`MADV_NOHUGEPAGE` constants and a no-op `pthread_attr_setaffinity_np()` fallback when unavailable.

Control flow: no runtime control flow; provides compile-time declarations and compatibility definitions.

State and persistence: declares external process-global benchmark state owned elsewhere.

Dependencies and integration: included by almost every perf bench implementation and by bench command dispatch code.

Risks: function declarations must remain synchronized with implemented benchmarks and command tables. The affinity fallback silently disables requested affinity on platforms without `pthread_attr_setaffinity_np`.

Test signals: full perf bench build across libc/platform variants and command dispatch for every declared benchmark.
