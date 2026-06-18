<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config

## Purpose
Declares kernel config prerequisites for uevent filtering tests.

## Important APIs, Types, and Functions
CONFIG_USER_NS=y, CONFIG_NET=y.

## Control Flow
Static kselftest config fragment only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Used by kselftest config merge tooling.

## Risks and Edge Cases
Incomplete configs can still fail at runtime if root or sysfs support is missing.

## Test Signals
Config tooling should request user and network namespace support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/config -->
