# sources/distributed-fs/ceph-client/tools/perf/util/evsel.c

## Purpose

`evsel.c` is the main perf event-selector implementation. It turns parsed event requests into initialized `struct evsel` objects, configures `perf_event_attr`, opens perf event file descriptors across CPU/thread maps, reads counts, parses sample records, names events for user output, records event IDs, and applies compatibility fallbacks for older kernels and PMUs.

## Important APIs, Types, and Functions

The file implements `evsel__object_config`, `evsel__init`, `evsel__new_idx`, `evsel__clone`, `evsel__newtp_idx`, `evsel__config`, `evsel__open`, `evsel__close`, `evsel__read_counter`, `evsel__parse_sample`, `evsel__fallback`, `evsel__open_strerror`, `evsel__store_ids`, group helpers, hybrid helpers, and event-name helpers. It owns the global `struct perf_missing_features perf_missing_features`, hardware/software/cache name tables, BPF counter event matching, and weak architecture hooks such as `arch_evsel__hw_name`, `arch__post_evsel_config`, `arch_evsel__set_sample_weight`, and `arch_evsel__open_strerror`.

## Control Flow

Construction starts with libperf `perf_evsel__init`, local defaults, list initialization, optional BPF output and clock-event adjustment, and deep-copy support for parsed-but-unopened selectors. `evsel__config` then combines record options, callchain options, per-event config terms, sample bits, mmap/comm/task tracking, branch stack settings, read formats, inherit behavior, clock IDs, and special off-CPU/dummy/AUX constraints. Opening uses `__evsel__prepare_open`, dispatches tool/hwmon/DRM/TPEBS PMUs to specialized open paths, otherwise loops CPU map indexes and thread indexes through `sys_perf_event_open`, attaching BPF fds and test-attribute logging when enabled. On failure it can remove vanished threads, raise `RLIMIT_NOFILE`, probe missing kernel features, reduce `precise_ip`, close partially opened descriptors, and mark the event unsupported.

Counter reads dispatch to tool/hwmon/DRM/TPEBS/group/single read paths. Group reads require IDs and map each returned ID back through the evlist. Sample parsing follows perf sample ABI order, initializes a `perf_sample`, handles non-sample `sample_id_all` trailers, and bounds-checks every variable-length region before exposing pointers to raw data, callchains, branch stacks, register dumps, stacks, AUX samples, and off-CPU synthesized samples.

## State and Persistence Behavior

Persistent object state lives in `struct evsel`: copied strings, config terms, cgroup references, PMU pointer, fd arrays, counts, previous counts for deltas, per-package masks, side-band callback data, BPF handles, stats, branch-counter metadata, and fallback flags. Global state includes missing-feature probes, cached empty CPU/thread maps, a process-wide clock ID used for errors, and optional private destructors. Runtime kernel resources are perf fds, IDs, BPF attachments, TPEBS resources, and count arrays; `evsel__exit` releases them and frees owned strings and hashmaps.

## Dependencies and Integration Points

This file integrates with libperf (`perf_evsel`, CPU/thread maps), `perf_event_open`, PMU discovery, BPF counters and filters, evlists, stats, histograms, callchains, trace-event parsing, tool PMUs, hwmon/DRM PMUs, Intel TPEBS, cgroups, procfs/sysfs, perf session/env metadata, and architecture-specific hooks. It is used by perf record/stat/report/script/top paths as the common event abstraction.

## Risks and Edge Cases

The highest-risk areas are kernel ABI compatibility probing, sample layout ordering, cross-endian decoding, group read ID matching, hybrid PMU CPU-map remapping, partial-open cleanup, mutable fallback names, and ownership of copied config strings. Incorrect `sample_size` or missing overflow checks can corrupt parsing. Fallbacks can silently change event semantics from hardware cycles to software clocks or from kernel-inclusive to user-only sampling. Feature detection mutates global flags and must preserve `errno` carefully.

## Test Signals

Useful tests include perf attr tests via `PERF_TEST_ATTR`, event open smoke tests for system-wide and per-thread modes, vanished-thread handling, group read with `PERF_FORMAT_ID`, sample parser tests for every sample bit and malformed sizes, cross-endian perf.data parsing, branch stack hardware-index/counter coverage, hybrid PMU stat output, precise-IP fallback, paranoid/EACCES fallback, BPF attachment, cgroup events, and old-kernel missing-feature probes.
