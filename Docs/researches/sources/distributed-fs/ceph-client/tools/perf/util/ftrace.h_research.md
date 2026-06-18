# sources/distributed-fs/ceph-client/tools/perf/util/ftrace.h

## Purpose

`ftrace.h` defines perf's ftrace command state and the optional BPF latency helper API used for function tracing and latency profiling.

## Important APIs, Types, and Functions

`struct perf_ftrace` stores the evlist, target, tracer name, filter/notrace/graph filter lists, event-pair list, profile hash, per-CPU buffer size, inherit/use-nsec options, histogram bucket settings, latency bounds, empty-bucket hiding, graph depth, stack/IRQ/args/retval/retaddr/nosleep/noirq/verbose/thresh/tail graph options, and BPF profile state. `struct filter_entry` stores flexible-array filter names. `NUM_BUCKET` defines the latency histogram bucket count. BPF helper prototypes are real when `HAVE_BPF_SKEL` is enabled and inline `-1` stubs otherwise.

## Control Flow

Perf ftrace code fills `perf_ftrace` from command options, configures kernel ftrace or BPF latency tracing, runs tracing, reads latency buckets/stats, then cleans up. The header itself only provides state layout and compile-time dispatch for BPF skeleton availability.

## State and Persistence Behavior

All struct fields are runtime command state. Lists hold filter entries and event pairs. `profile_hash` likely stores per-function profiling data. The fallback inline BPF functions do not mutate state and signal unsupported operation with `-1`.

## Dependencies and Integration Points

It depends on Linux list heads, perf target handling, evlists, hashmaps, stats, and optional BPF skeleton support. It is used by ftrace builtin/util implementation files.

## Risks and Edge Cases

There is a typo forward declaration `struct hashamp;` while the field uses `struct hashmap`; this is harmless if another declaration is visible but suspicious. Callers must initialize list heads and defaults before use. Builds without BPF skeletons must handle `-1` returns cleanly.

## Test Signals

Compile tests with and without `HAVE_BPF_SKEL`, option initialization tests, ftrace graph option smoke tests, latency histogram bucket tests, and BPF unsupported-path tests are useful signals.
