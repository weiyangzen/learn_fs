# sources/distributed-fs/ceph-client/tools/perf/bench/syscall.c

Purpose: implements the `perf bench syscall` sub-benchmarks for `getppid`, `getpgid`, `fork`, and `execve`. It runs a selected syscall workload for a loop count and reports total elapsed time plus per-operation performance.

Important APIs, types, and functions: `loops` is configured by `--loop` after each workload sets a default. `test_fork()` forks and waits for a child that exits immediately. `test_execve()` forks, the child executes `/bin/true`, and the parent waits. `bench_syscall_common()` centralizes option parsing, timing, workload dispatch, name selection, and output. The exported bench entry points are `bench_syscall_basic()`, `bench_syscall_getpgid()`, `bench_syscall_fork()`, and `bench_syscall_execve()`.

Control flow: the wrapper passes a syscall number to `bench_syscall_common()`. Fork and exec defaults use 10000 loops to limit runtime; simple syscalls default to 10000000. Each iteration calls the relevant libc or syscall-related helper. After timing, a switch maps the syscall number to a printable name, and output follows `BENCH_FORMAT_DEFAULT` or `BENCH_FORMAT_SIMPLE`.

State and persistence: no persistent state is written. Fork and exec temporarily create child processes; exec assumes `/bin/true` exists and is executable. Locale-aware grouping is used in printf format strings if the caller configured locale in the bench frontend.

Dependencies and integration points: included by `builtin-bench.c` under the `syscall` collection. It uses perf bench output globals and standard Linux process APIs.

Risks: the `case __NR_execve:` branch lacks an explicit `break` before `default`, currently harmless because default is empty but fragile. `__NR_fork` may be `-1` on architectures without a fork syscall number, yet the benchmark wrapper still passes it and the switch may behave unexpectedly. `/bin/true` is hard-coded. Child failures call `exit(1)`, terminating the benchmark process path. Very high loop counts can heavily load the system.

Test signals: run each syscall benchmark with `-l 1` and a modest loop count, verify simple and default formats, test on architectures with and without `__NR_fork`, and validate `/bin/true` failure behavior in constrained environments.
