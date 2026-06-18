# sources/distributed-fs/ceph-client/tools/perf/tests/keep-tracking.c

## Purpose
Integration test for using a dummy software event to keep tracking records alive while another event is disabled.

## Important APIs, Types, and Functions
- `find_comm(struct evlist *evlist, const char *comm)` scans mmap buffers and counts `PERF_RECORD_COMM` events for the current pid/tid and requested comm.
- `test__keep_tracking()` creates thread/cpu maps, parses `dummy:u` and `cpu-cycles:u`, configures mmap recording, sets the dummy evsel to track comm events while initially disabled, opens/mmaps/enables/disables events, and uses `prctl(PR_SET_NAME, ...)` to generate comm records.
- Local `CHECK__` and `CHECK_NOT_NULL__` macros funnel failures to cleanup.

## Control Flow
The test creates maps for the current tid and online CPUs, builds an evlist with dummy and cycles events, configures record options, sets the first evsel (`dummy`) to record comm events with `disabled=1` and no `enable_on_exec`, then opens and mmaps. First it enables the whole evlist, changes comm to `"Test COMM 1"`, disables the evlist, and expects one comm record. Second it enables the evlist, disables only the last evsel (`cpu-cycles`), changes comm to `"Test COMM 2"`, disables the evlist, and again expects one comm record, proving dummy tracking remained active.

## State and Persistence
State is kernel perf event fds/mmap buffers plus the process comm name changed by `prctl()`. The evlist is disabled/deleted on cleanup, and maps are put. No files are written.

## Dependencies and Integration Points
Uses parse-events, evlist config/open/mmap/enable/disable, evsel disable, perf mmap read APIs, record options, and Linux `prctl`. Registered as `DEFINE_SUITE("Use a dummy software event to keep tracking", keep_tracking)`.

## Risks and Edge Cases
- Requires permission to open dummy and hardware cycle events; otherwise it skips.
- The test changes the current thread comm and does not restore the original name.
- It assumes exactly one comm record is present for each generated name in the mmap buffers.

## Test Signals
Passing confirms tracking events are emitted both when the whole group is enabled and when the non-dummy event is disabled. Failure indicates missing comm records or setup/open/mmap errors.
