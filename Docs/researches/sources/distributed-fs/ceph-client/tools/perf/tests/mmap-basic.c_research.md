# sources/distributed-fs/ceph-client/tools/perf/tests/mmap-basic.c

## Purpose
Tests perf mmap sample delivery for syscall tracepoints and user-space counter reading through the perf event mmap page.

## Important APIs, Types, and Functions
- `test__basic_mmap()` opens tracepoint evsels for `sys_enter_getsid`, `sys_enter_getppid`, and `sys_enter_getpgid`, mmaps events, invokes syscalls random counts, reads samples, maps sample ids back to evsels, and checks counts.
- `enum user_read_state` and `set_user_read()` read/write PMU `rdpmc` sysfs controls when available.
- `test_stat_user_read(u64 event, enum user_read_state enabled)` scans core PMUs, opens a hardware event, mmaps it, validates `perf_event_mmap_page` user-read capabilities, reads counts, runs busy loops, and verifies monotonic count deltas.
- Four wrappers test instructions/cycles with user reading enabled or disabled.

## Control Flow
The basic mmap test binds the process to the first online CPU, creates per-thread tracepoint events with wakeup events and sample IDs, maps the evlist, generates syscalls, drains mmap records, parses samples, counts by evsel index, and compares observed counts to generated counts. The user-read tests create a dummy thread map, iterate core PMUs, optionally change rdpmc state, restrict affinity to PMU CPUs, open/mmap an evsel, validate mmap page flags/index/width against expected support, read initial and loop counts, then close/unmap and restore rdpmc and affinity.

## State and Persistence
State includes kernel perf event fds, mmap buffers, process CPU affinity, and optionally sysfs `rdpmc` settings that are restored per PMU. No repository files are changed. The basic test uses `rand()` for expected counts but records them before generating syscalls.

## Dependencies and Integration Points
Integrates tracepoint evsel creation, evlist mmap/read/sample parsing, id-to-evsel lookup, PMU scanning, libperf evsel mmap APIs, CPU affinity helpers, and architecture-specific user counter support. Registered as `suite__basic_mmap`.

## Risks and Edge Cases
- Requires tracepoint and perf_event permissions; many failure paths are reported as skips or failures depending on stage.
- Affinity changes can fail on constrained environments.
- User-read behavior depends on architecture, PMU sysfs, hybrid PMU semantics, and kernel support for `cap_user_rdpmc`.
- The busy-loop monotonic check is basic and does not assert exact event counts.

## Test Signals
Passing proves mmap sample delivery can be parsed and attributed to evsels, and user-space counter access flags/counts match enabled/disabled expectations for supported architectures.
