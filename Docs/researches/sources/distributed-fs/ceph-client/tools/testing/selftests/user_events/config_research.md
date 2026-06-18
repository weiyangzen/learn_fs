<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config

## Purpose
Declares CONFIG_USER_EVENTS as the required kernel option for user_events tests.

## Important APIs, Types, and Functions
CONFIG_USER_EVENTS=y.

## Control Flow
Static config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumed by kselftest config tooling.

## Risks and Edge Cases
Runtime still requires root and tracefs even if config is enabled.

## Test Signals
Config merge should request user_events support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/user_events/config -->
