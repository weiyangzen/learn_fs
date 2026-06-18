# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/config

## Purpose
Declares kernel options required for sw_sync selftests.

## Important APIs, types, and functions
Contains `CONFIG_STAGING=y` and `CONFIG_SW_SYNC=y`.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling so the staging sw_sync driver is enabled.

## Risks
Without these options the built userspace tests cannot exercise `/dev/sw_sync` behavior.

## Test signals
The config entries identify the kernel support expected before running sync tests.
