# sources/distributed-fs/ceph-client/tools/tracing/latency/latency-collector.c

## Purpose
`latency-collector.c` is a standalone ftrace latency collector. It configures a selected latency tracer, watches `tracing_max_latency` with inotify, and prints snapshots of the trace file when new maximum latencies occur. It is designed to catch clusters of close latencies by optionally delaying trace reads with controlled randomization so the program does not always print only the first event in a burst.

## Important APIs, Types, and Functions
Important state includes selected tracer, ftrace option state, scheduling policy/priority, trace file paths, threshold, random sleep settings, verbosity, signal flag, and print-thread count. `struct ftrace_state` stores original tracer, threshold, and trace options for restoration. `struct print_state`, `struct queue`, and `struct entry` implement ordered request/ticket handling. Key functions include `scan_arguments()`, `find_default_tracer()`, `save_and_disable_tracer()`, `enable_tracer()`, `restore_ftrace()`, `cleanup_exit()`, `tracing_loop()`, `do_printloop()`, `print_tracefile()`, `set_priority()`, and queue/probability-table helpers.

## Control Flow
`main()` initializes save state and signals, opens stdout unbuffered, parses options, shows parameters, initializes print state, probability table if needed, sets scheduler priority, starts print threads, then enters `tracing_loop()`. The loop optionally saves/restores ftrace state around tracer setup, resets max latency, watches `debug_maxlat`, starts tracing, then reads inotify events. Each modification creates a ticketed request unless another print is ongoing or the bounded queue is full. Print threads consume queue entries, decide whether to sleep randomly, print skip/lost messages when races occur, or read `debug_tracefile` into a large buffer and write it atomically under `print_mtx`.

## State and Persistence
The utility changes global ftrace files: `current_tracer`, `tracing_thresh`, `tracing_max_latency`, and `trace_options`. Original values are saved and restored on cleanup unless `--no-ftrace`, `--tracefile`, or `--max-lat` puts the tool in externally managed mode. It may change its scheduler policy. Long-lived runtime state is in mutex-protected queues, counters, probability table, and thread-local random buffers.

## Dependencies and Integration Points
The code depends on libtracefs, pthreads, inotify, ftrace latency tracers (`preemptirqsoff`, `preemptoff`, `irqsoff`, wakeup variants), `/dev/urandom`, POSIX scheduling, and Linux tracing files. It integrates with kernel tracing by file writes/reads through libtracefs and direct `open/read` of the trace file.

## Risks and Edge Cases
Running as root or with tracing permissions is typically required. The program exits rather than restoring if it decides another tracer is active and `--force` is absent, leaving any state already changed before that point minimal but worth checking. The queue is intentionally small, so fast bursts can lose print requests. `print_tracefile()` uses a fixed 16 MiB buffer and truncates if the trace is larger than available space. Cleanup tries to lock the print mutex for one second but proceeds even if output races remain. The ring/ticket logic is intricate; missed-event messages depend on verbosity. Some `malloc_or_die_nocleanup()` paths avoid cleanup from restoration code to prevent recursion.

## Test Signals
Test `--list`, default tracer selection, invalid tracer, `--force`, `--no-ftrace`, custom trace/max-lat paths, immediate and random print modes, queue saturation, signal cleanup, and priority bounds. Use tracefs fixtures or a live kernel to verify original ftrace settings are restored and that trace output includes BEGIN/END markers and maximum latency summary.
