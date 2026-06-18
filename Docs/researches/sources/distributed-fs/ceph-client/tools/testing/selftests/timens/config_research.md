# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/config

## Purpose
Kselftest config fragment requiring time namespace support.

## Important APIs, Types, and Functions
Contains `CONFIG_TIME_NS=y`.

## Control Flow
No executable flow; consumed by selftest config tooling.

## State and Persistence Behavior
Static kernel configuration requirement only.

## Dependencies and Integration Points
Integrates with all tests under `tools/testing/selftests/timens` that rely on `CLONE_NEWTIME` and `/proc/self/ns/time`.

## Risks and Edge Cases
The config option does not guarantee the test runner has permissions to create time namespaces.

## Test Signals
Signal is kernel config coverage for `CONFIG_TIME_NS=y`.
