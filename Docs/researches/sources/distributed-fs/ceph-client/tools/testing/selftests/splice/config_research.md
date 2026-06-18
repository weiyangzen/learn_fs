# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/config

## Purpose
Declares kernel config dependency for splice selftests.

## Important APIs, types, and functions
Contains `CONFIG_TEST_LKM=m`, requesting the test loadable kernel module.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling to identify kernel module requirements.

## Risks
If the module is not built or loadable, sysfs splice checks in `short_splice_read.sh` may fail or skip indirectly.

## Test signals
Presence of the config line signals the expected test module requirement.
