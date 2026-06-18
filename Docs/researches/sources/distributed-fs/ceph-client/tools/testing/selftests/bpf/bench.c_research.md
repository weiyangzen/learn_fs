# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.c

## Purpose

`bench.c` is the generic userspace driver for BPF benchmarks. It parses global and benchmark-specific options, chooses a registered `struct bench`, starts producer/consumer threads, samples once per second, and prints progress/final throughput summaries.

## Important APIs, Types, and Functions

Global state is `struct env env`, `const struct bench *bench`, and internal `state`. Core functions include `setup_libbpf()`, reporting helpers for hits/drops, operations, false hits, local storage, and grace-period stats, command-line parsers, `setup_timer()`, `set_thread_affinity()`, `next_cpu()`, `find_benchmark()`, `setup_benchmark()`, `collect_measurements()`, and `main()`. It declares every benchmark object linked from `benchs/`.

## Control Flow and Data Flow

`main()` discovers CPU count, parses global options, lists benchmarks if requested, selects a benchmark by name, reparses with that benchmark's argp, validates and sets it up, creates requested consumer and producer threads, starts an interval timer, then waits on a condition variable. SIGALRM drives `collect_measurements()`, which asks the active benchmark to fill `bench_res`, prints progress, and signals completion after warmup plus duration. Final reporting skips warmup samples.

## State and Persistence Behavior

Runtime state includes allocated arrays for thread IDs and per-second results, CPU affinity cursors, benchmark-specific global state in linked modules, and process signal/timer state. It writes no files.

## Dependencies and Integration Points

It depends on pthreads, argp, libbpf strict mode and print callbacks, `testing_helpers`, CPU-list parsing, kselftest BPF benchmark modules, and POSIX interval timers.

## Risks and Edge Cases

The timer handler calls benchmark measurement and printing paths from signal context, which is pragmatic for this tool but not async-signal-safe in the strict POSIX sense. Producers run infinite loops and are not joined. CPU-list validation fails late if too few CPUs are provided. Final latency calculations assume nonzero throughput.

## Test Signals

`bench -l` should list all registered benchmarks. Running a simple benchmark such as `count-local` should produce per-second progress and a final summary; BPF-backed benchmarks additionally validate skeleton load/attach and helper reporting.
