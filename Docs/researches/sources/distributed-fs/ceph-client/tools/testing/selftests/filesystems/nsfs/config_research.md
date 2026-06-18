# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/config

## Purpose

This config fragment declares namespace features required by the nsfs tests.

## Important APIs, Types, and Functions

It requires `CONFIG_USER_NS=y`, `CONFIG_UTS_NS=y`, and `CONFIG_PID_NS=y`.

## Control Flow, State, and Persistence

There is no control flow. The fragment is static test configuration metadata.

## Dependencies, Integration Points, Risks, and Test Signals

The owner test needs user and UTS namespaces; the pidns test needs user and PID namespaces. Without these options, the binaries cannot exercise target nsfs ioctls. Passing signals are successful namespace creation and no skip/failure due to unavailable namespace types.
