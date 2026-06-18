# Research: sources/distributed-fs/ceph-client/tools/perf/bench/evlist-open-close.c

Purpose: benchmarks perf evlist creation, opening, mmaping, enabling/disabling, unmapping, and closing for a configurable event expression and target.

Important APIs/types/functions: `bench_evlist_open_close()` parses options. `bench__repeat_event_string()` clones event selectors. `bench__create_evlist()` parses events, applies UID filtering, creates maps, and configures evlist. `bench__do_evlist_open_close()` exercises open/mmap/enable/disable/munmap/close. `bench_evlist_open_close__run()` runs iterations and reports average/stddev.

Control flow: parse target/event options, validate target, enable missing-thread tolerance for pid targets, expand event string, print event/cpu/thread/fd counts from a first evlist, then create and destroy a new evlist for each timed iteration.

State and persistence: static `record_opts` mirrors perf record defaults used for evlist config. Runtime evlists are allocated per iteration and deleted. No files persist.

Dependencies and integration: depends on parse-events, evlist/evsel APIs, record options, target validation, UID parsing, perf cpumap/threadmap, mmap handling, stats, and debug/error utilities.

Risks: failures after `evlist__mmap()` in `bench__do_evlist_open_close()` return without local cleanup, relying on caller deletion. Event repetition can build large selector strings. Results are sensitive to permissions, target lifetimes, and CPU/thread map size.

Test signals: dummy event defaults, repeated events, system-wide and CPU-list modes, pid/tid/uid/per-thread targets, invalid event strings, and low permission `perf_event_open` behavior.
