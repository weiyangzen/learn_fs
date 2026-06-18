<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h

## Purpose

`intel-tpebs.h` declares the small interface that lets evsel/perf-stat code use TPEBS retirement-latency sampling when enabled.

## Important APIs, Types, and Functions

`enum tpebs_mode` selects aggregation: mean, min, max, or last. `tpebs_recording` enables the feature and `tpebs_mode` selects the read behavior. The API consists of `evsel__tpebs_open()`, `evsel__tpebs_close()`, and `evsel__tpebs_read()`.

## Control Flow

Callers open TPEBS around retire-latency evsel open, read a synthesized latency count from the first CPU/thread slot during stat reads, and close when the evsel is closed. The implementation in `intel-tpebs.c` owns the child process and reader thread.

## State and Persistence Behavior

The header exposes process-global mode state but no persistent storage. The underlying implementation stores sampled stats in memory only.

## Dependencies and Integration Points

It forward-declares `struct evlist` and `struct evsel` and is included by evsel/stat paths that need optional TPEBS hooks.

## Risks and Edge Cases

Callers must gate by `tpebs_recording` and use only retire-latency evsels. The enum order is used by command-line parsing and should remain stable.

## Test Signals

Compile tests should ensure non-TPEBS builds still see declarations. Runtime tests should check every `tpebs_mode` and open/read/close symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.h -->
