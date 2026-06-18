<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c

## Purpose
Tests user_events as perf tracepoints by attaching perf_event_open and reading raw samples from the perf mmap buffer.

## Important APIs, Types, and Functions
perf_event_open syscall wrapper, get_id, get_offset, clear, PERF_TYPE_TRACEPOINT, PERF_SAMPLE_RAW.

## Control Flow
Registers an event, obtains its tracepoint id and field offset from tracefs, opens a perf event, mmaps the perf page, writes user event data, and checks sample record type plus payload values; repeats for empty events.

## State and Persistence
Creates tracefs event, perf fd/mmap buffer, and updates enable bits through perf attachment; cleans event in teardown.

## Dependencies and Integration Points
Requires root, tracefs, perf_event_open permissions, CONFIG_USER_EVENTS, and kselftest harness.

## Risks and Edge Cases
Direct perf ring parsing assumes sample layout and immediate visibility; restricted perf_event_paranoid can block runtime.

## Test Signals
Pass means perf receives expected samples and status bits clear after perf fd close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/perf_test.c -->
