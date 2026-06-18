# sources/distributed-fs/ceph-client/tools/perf/builtin-bench.c

Purpose: implements the top-level `perf bench` command. It registers benchmark collections and individual benchmarks, parses common output/repeat options, prints usage, and dispatches to the selected benchmark function.

Important APIs, types, and functions: `bench_fn_t`, `struct bench`, and `struct collection` define the registry. Static arrays describe `sched`, `syscall`, `mem`, `numa`, `futex`, `epoll`, `internals`, `breakpoint`, and `uprobe` collections, with conditional compilation for optional libraries. `bench_format` and `bench_repeat` are exported globals consumed by benchmark modules. `dump_benchmarks()`, `print_usage()`, `bench_str2int()`, `run_bench()`, `run_collection()`, `run_all_collections()`, and `cmd_bench()` implement the frontend.

Control flow: `cmd_bench()` sets stdout unbuffered, configures locale, parses common options until the first non-option, validates format and repeat, then dispatches. `all` runs all collections; `<collection> all` runs every benchmark in one collection; `<collection> <benchmark>` renames the task via `prctl(PR_SET_NAME)` and calls the function with adjusted argv. Missing collection or benchmark prints contextual help.

State and persistence: persistent state is not written. Process state includes locale, stdout buffering, process comm name, and global `bench_format`/`bench_repeat`. Individual benchmarks may create their own external effects.

Dependencies and integration points: includes `bench/bench.h`, which declares all benchmark functions. It is the central integration point for the bench files in this subset: sched pipe, seccomp notify, synthesize, syscall, and uprobe are all reachable through this registry.

Risks: collection `all` can call entries whose `benchmarks` pointer is NULL, relying on `for_each_bench` short-circuit behavior. Optional collections depend on compile-time macros and can alter user-visible availability. `run_collection()` supplies minimal argv, so benchmarks must tolerate defaults. `bench_repeat` is validated but not used by all benchmarks. Process name allocation uses `BUG_ON` on allocation failure.

Test signals: run `perf bench`, unknown collection, unknown benchmark, each collection help path, `--format default/simple`, invalid format, `--repeat 0`, `all`, and representative individual benchmarks. Confirm conditional collections appear only when compiled in.
