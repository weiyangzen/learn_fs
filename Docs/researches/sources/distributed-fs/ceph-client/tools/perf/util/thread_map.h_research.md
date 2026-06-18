# sources/distributed-fs/ceph-client/tools/perf/util/thread_map.h

## Purpose

`thread_map.h` declares perf's thread-map constructors and helpers.

## Important APIs, Types, and Functions

It exports constructors from PID, TID, PID/TID strings, recorded thread-map events, and the dummy map path through `thread_map__new_dummy()` from another implementation. It also exports formatting, comm reading, membership, and removal helpers.

## Control Flow and State

The header has no implementation state. It establishes that callers work with `struct perf_thread_map` from libperf and perf record thread-map events.

## Dependencies and Integration Points

It includes `<perf/threadmap.h>` and is consumed by event opening, stat, record, and replay paths.

## Risks and Test Signals

Compile tests should catch ABI changes to `perf_thread_map`. Behavioral tests belong in the implementation and should verify ownership of returned maps and comm strings.
