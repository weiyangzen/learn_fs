# sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/sample-raw.h` declares architecture-specific raw sample callbacks and the selector that installs them on an evlist.

## Important APIs, Types, and Functions

It forward-declares `struct evlist`, `union perf_event`, and `struct perf_sample`. Declared functions are `evlist__s390_sample_raw`, `evlist__has_amd_ibs`, `evlist__amd_sample_raw`, and `evlist__init_trace_event_sample_raw`.

## Control Flow

The header has no executable flow. It establishes the callback signatures used by raw sample display code.

## State and Persistence Behavior

No state is owned by the header. Implementations mutate evlist callback state or print raw sample data.

## Dependencies and Integration Points

It connects generic sample raw initialization with s390 and AMD IBS implementations.

## Risks and Edge Cases

The closing include-guard comment names `__PERF_EVLIST_H`, which is only a comment mismatch but can confuse maintainers. Callers must pass samples whose raw data layout matches the selected callback.

## Test Signals

Compile coverage and selector tests from `sample-raw.c` validate this header.
