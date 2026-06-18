<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c

## Purpose
Tests user_events ftrace integration: registration semantics, writev data emission, fault handling, dynamic string validation, and generated print_fmt strings.

## Important APIs, Types, and Functions
trace_bytes, get_print_fmt, clear, check_print_fmt, DIAG_IOCSREG/UNREG/DEL, writev, DYN_LOC.

## Control Flow
Registers __test_event formats, toggles enable files, writes event payloads through user_events_data, checks ftrace trace size growth, validates invalid slot/disabled/negative index errors, exercises dynamic string bounds and null termination, and compares print_fmt output.

## State and Persistence
Creates tracefs events, opens status/data/enable files, writes trace buffer data, and cleans/deletes events in teardown.

## Dependencies and Integration Points
Requires root, tracefs, CONFIG_USER_EVENTS, ftrace event files, kselftest harness.

## Risks and Edge Cases
Trace buffer byte-count checks can be noisy if other tracing is active; exact print_fmt strings are ABI-sensitive.

## Test Signals
Pass means write paths and generated formats match expected behavior and all invalid writes fail with expected errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/ftrace_test.c -->
