# sources/distributed-fs/ceph-client/tools/perf/util/evsel.h

## Purpose

`evsel.h` declares perf's higher-level event-selector object and its public utility API. It wraps libperf `struct perf_evsel` with perf-tool state used by parsing, recording, counting, reporting, BPF integration, metrics, grouping, and sample decoding.

## Important APIs, Types, and Functions

The central type is `struct evsel`. It embeds `struct perf_evsel core` and adds parsed names, tracepoint metadata, filters, config terms, metric links, count storage, stats, flags, BPF counter state, PMU pointer, fallback state, start-time storage for tool PMUs, and branch-counter metadata. `struct perf_missing_features` records kernel/PMU ABI capabilities that have been probed or disabled. The header exposes constructors/destructors, config/open/read/parse APIs, sample-bit helpers, group iteration macros, name/metric helpers, tracepoint field helpers, fallback/error helpers, leader/group utilities, hybrid and AUX helpers, and PMU config get/set helpers.

## Control Flow

Consumers typically parse an event into an `evsel`, call `evsel__config`, open it with CPU/thread maps, optionally store IDs into an evlist, read counters or parse records, and finally close/delete it. The inline helpers keep sample-bit mutations synchronized with `sample_size`/ID positions through the C implementation. Group iteration macros rely on contiguous evlist ordering and matching leader pointers.

## State and Persistence Behavior

The header defines ownership boundaries that implementations must respect: copied strings in the anonymous parse-state struct, list-owned config terms, refcounted cgroups/maps, BPF objects/fds, count arrays, optional per-package hashmaps, and a tool-specific `priv` pointer guarded by a global destructor. Many booleans are durable per-selector policy, such as `tracking`, `supported`, `disabled`, `skippable`, `forced_leader`, and fallback markers.

## Dependencies and Integration Points

It depends on Linux perf ABI headers, libperf internal/public evsel headers, CPU/thread maps, PMU metadata, symbol configuration, traceevent types when available, BPF skeleton forward declarations, `hashmap`, stats, record options, and target definitions. It is included across perf util and builtin code as the primary contract for event selection.

## Risks and Edge Cases

Because the struct is large and manually cloned/freed, any new owned field must be added to clone and teardown logic. The anonymous struct comments explicitly warn parse-time fields need clone handling. Group macros assume list layout; misuse outside an evlist can walk invalid memory. The pointer/integer mix around `hashmap` and BPF state requires precise ownership discipline.

## Test Signals

Header-level regressions show up as compile failures in perf builtins, clone/free leaks, group iteration errors, and sample parser mismatches. Tests should cover adding config-term types, struct-size extension through `evsel__object_config`, event grouping, BPF/bperf predicates, and synthesized sample-type behavior.
