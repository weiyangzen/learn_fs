# sources/distributed-fs/ceph-client/tools/perf/util/thread_map.c

## Purpose

`thread_map.c` builds and manipulates `perf_thread_map` objects from PIDs, TIDs, procfs scans, or recorded thread-map events. These maps drive perf event opening and aggregation over selected threads.

## Important APIs, Types, and Functions

Constructors include `thread_map__new_by_pid()`, `thread_map__new_by_tid()`, `thread_map__new()`, `thread_map__new_str()`, `thread_map__new_by_tid_str()`, and `thread_map__new_event()`. Utility functions are `thread_map__fprintf()`, `thread_map__read_comms()`, `thread_map__has()`, and `thread_map__remove()`. Internal helpers scan `/proc/<pid>/task`, all `/proc` task directories, and `/proc/<tid>/comm`.

## Control Flow and State

PID-based creation expands each process to its task list. TID-based creation creates explicit entries or a dummy map when no TID string is supplied. All-thread mode scans all numeric `/proc` directories and grows the map as needed. Event-based creation reconstructs pids and comm strings from `PERF_RECORD_THREAD_MAP`. `thread_map__remove()` frees the removed comm and shifts later entries.

## Dependencies and Integration Points

It depends on procfs, `strlist`, `perf_thread_map__realloc`, internal thread-map accessors, and perf event record formats. It integrates with target parsing, evlist open paths, stat output, and perf.data replay.

## State and Persistence Behavior

Maps are heap objects with refcounts initialized to one. Comm strings are optional and best-effort; failing to read a comm emits a warning but still leaves a usable thread map. Recorded thread maps preserve 16-byte comm strings from perf.data.

## Risks and Test Signals

Risks include races with exiting tasks, duplicate input IDs, unbounded all-thread scans, and partial allocation failures. Tests should cover PID expansion, TID lists, null TID dummy behavior, all-thread scans under disappearing tasks, comm loading, event round-trip, and removal edge cases.
