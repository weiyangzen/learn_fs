# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/inlineloop.c

## Purpose
This workload creates an always-inlined call chain inside a bounded CPU loop so perf can test inline call attribution and symbol reporting.

## Important APIs, Types, And Functions
It defines `leaf()` and `middle()` as `static inline __attribute__((always_inline))`, `parent()` as `noinline`, and workload entry `inlineloop()`. It uses `pthread_setname_np()`, `signal()`, `alarm()`, `atoi()`, and `DEFINE_WORKLOAD(inlineloop)`.

## Control Flow
`inlineloop()` sets a recognizable thread name, parses duration, installs signal handlers, arms an alarm, and calls `parent(sec)`. `parent()` calls `middle()`, which inlines `leaf()`. `leaf()` loops with a `goto` label, incrementing volatile `a` until the signal handler sets `done`.

## State, Dependencies, And Integration
State consists of volatile integer `a` and `volatile sig_atomic_t done`. The function attributes create an expected profile shape: a non-inlined parent with inline children. Integration is through perf workload registration and downstream script/report tests.

## Risks And Test Signals
Compiler behavior is central: changing attributes or optimization flags can destroy the intended inline stack. A good signal is perf output showing samples in `parent` with inline frames for `middle`/`leaf` according to debug info.
