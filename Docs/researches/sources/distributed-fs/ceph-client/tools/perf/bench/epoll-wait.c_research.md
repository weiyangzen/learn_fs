# Research: sources/distributed-fs/ceph-client/tools/perf/bench/epoll-wait.c

Purpose: benchmarks `epoll_wait(2)` throughput with eventfd producers under single shared queue or one-queue-per-worker models, with optional edge-triggered, one-shot, nonblocking, nested, and randomized behavior.

Important APIs/types/functions: `bench_epoll_wait()` orchestrates the run. `do_threads()` creates worker epoll registrations and optional CPU affinity. `workerfn()` performs one-event `epoll_wait`, reads eventfd data, and re-adds or rearms for EPOLLET/EPOLLONESHOT. `writerfn()` continuously writes to workers' fd maps. `shuffle()` supports random order. `print_summary()` aggregates throughput.

Control flow: under `HAVE_EVENTFD_SUPPORT`, setup parses options, configures SIGINT, creates epoll fd(s), defaults workers to online CPUs minus one, raises `RLIMIT_NOFILE`, starts workers behind a barrier, starts a writer thread, sleeps runtime seconds, toggles `done`, stops writer after a delay, joins, sorts randomized workers for output, and reports ops/sec.

State and persistence: process-global booleans configure mode and termination; per-worker state holds epoll fd, eventfds, thread id, and op count. No persistent files. Runtime uses many fds and threads.

Dependencies and integration: depends on eventfd/epoll/pthreads, perf cpumap, mutex/cond wrappers, stats, signal handling, and bench globals.

Risks: plain bool termination flags are shared with signal/thread contexts. Nonblocking mode can count iterations with no event if `epoll_wait` returns zero and `ev` is stale; default mode avoids that. Writer pressure and eventfd saturation can skew results. Nested epoll arrays are global even in multiq mode.

Test signals: single vs multiq, edge-triggered and one-shot rearm paths, nonblocking mode, nested epolls, random writer order, large fd counts, and build without eventfd support.
