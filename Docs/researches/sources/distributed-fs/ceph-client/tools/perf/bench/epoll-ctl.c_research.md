# Research: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-ctl.c

Purpose: benchmarks concurrent `epoll_ctl(2)` ADD/MOD/DEL operations against one shared epoll instance, optionally with nested epoll and randomized operations.

Important APIs/types/functions: `bench_epoll_ctl()` is the entry point. `do_threads()` creates workers, eventfds, optional CPU affinity, and initial random-mode fd registration. `workerfn()` performs deterministic or random `epoll_ctl` loops. `nest_epollfd()` builds nested epoll chains. `print_summary()` reports average operation counts with stats.

Control flow: only compiled under `HAVE_EVENTFD_SUPPORT`. The entry point parses options, installs SIGINT handler, creates the shared epoll fd, raises `RLIMIT_NOFILE`, starts workers behind a mutex/cond barrier, sleeps for runtime seconds, toggles `done`, joins workers, aggregates per-op stats, and frees fd maps.

State and persistence: static process globals track options, `done`, shared epoll fd, nesting fds, startup barrier state, and stats. No persistent files. File descriptors and worker arrays are runtime resources.

Dependencies and integration: depends on eventfd, epoll, pthreads, perf CPU map affinity, perf mutex/cond wrappers, stat helpers, and bench timing globals.

Risks: shared `done` is a plain bool written from a signal handler and read by threads. Nested epoll allocation has limited cleanup. Resource-limit changes affect the process. Random mode intentionally permits failed operations and counts only successes, so interpretation differs from deterministic mode.

Test signals: build with/without eventfd support, default CPU-count threads, `--randomize`, `--nested`, `--noaffinity`, high `--nfds`, SIGINT early stop, and leak/fd exhaustion checks.
