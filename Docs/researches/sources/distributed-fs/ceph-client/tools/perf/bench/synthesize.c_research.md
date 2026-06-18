# sources/distributed-fs/ceph-client/tools/perf/bench/synthesize.c

Purpose: implements `perf bench internals synthesize`, benchmarking perf's synthetic event generation for thread maps. It measures both single-threaded synthesis for the current process and multi-threaded synthesis for target CPU 0, reporting average runtime, standard deviation, event count, and time per event.

Important APIs, types, and functions: global options control `min_threads`, `max_threads`, `single_iterations`, `multi_iterations`, `run_st`, and `run_mt`. `process_synthesized_event()` is a dummy perf tool callback that increments `event_count`. `do_run_single_threaded()` invokes `__machine__synthesize_threads()` repeatedly against a fixed thread map. `run_single_threaded()` creates a perf session and `thread_map__new_by_pid(getpid())`. `do_run_multi_threaded()` creates a new session for each iteration and synthesizes without a prebuilt thread map. `run_multi_threaded()` toggles perf's single/multithreaded mode by requested worker count. `bench_synthesize()` dispatches selected modes.

Control flow: options are parsed and no positional arguments are accepted. If neither `--st` nor `--mt` is set, single-threaded mode is enabled. Single-threaded mode creates one session and one self pid thread map, then measures normal and data-mmap synthesis. Multi-threaded mode defaults `max_threads` to online CPUs, iterates from min to max, sets perf threading mode, and calls the synthesis helper for each thread count.

State and persistence: all state is in memory: perf sessions, perf environment, thread maps, stats accumulators, and an atomic event counter. No files are read beyond system proc/sysfs state needed by perf synthesis, and no output is persisted beyond stdout.

Dependencies and integration points: uses `util/session`, `synthetic-events`, `thread_map`, `target`, `stat`, `tool`, and perf thread-mode helpers. It is exposed by `builtin-bench.c` as `internals synthesize`.

Risks: large default `single_iterations` can be expensive. `max_threads < min_threads` silently produces no multi-threaded runs. Multi-thread mode targets CPU 0, so systems with unusual CPU availability can skew or fail. Division by `event_average` assumes synthesis emitted events. Error cleanup must delete sessions and release thread maps on all paths.

Test signals: run default mode, `--st`, `--mt -m 1 -M 2 -I 1`, and invalid positional arguments. Check that event counts are nonzero, sessions are deleted, and perf threading mode is restored to single-threaded after multi-threaded runs.
