<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h

## Purpose
Shared setup/teardown helpers for user_events tests that ensure root, tracefs mount, and user_events_data availability.

## Important APIs, Types, and Functions
tracefs_enabled, user_events_enabled, USER_EVENT_FIXTURE_SETUP, USER_EVENT_FIXTURE_TEARDOWN.

## Control Flow
Checks /sys/kernel/tracing, mounts tracefs if README is absent, verifies /sys/kernel/tracing/user_events_data, and unmounts tracefs in teardown only if this helper mounted it.

## State and Persistence
May mount and later unmount tracefs; communicates skip/fail state through message/fail/umount outputs.

## Dependencies and Integration Points
Depends on mount/umount, stat, errno, kselftest.h, root privileges.

## Risks and Edge Cases
Mounting tracefs in a shared environment can affect concurrent tests; root absence is treated as fail for user_events_enabled.

## Test Signals
Tests using the macros skip cleanly when user_events is absent and fail when tracefs cannot be accessed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/user_events_selftests.h -->
