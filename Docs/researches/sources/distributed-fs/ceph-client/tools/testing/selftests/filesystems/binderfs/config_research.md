# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/binderfs/config

## Purpose
Kernel config fragment for binderfs selftests.

## Important APIs, Types, And Functions
Sets `CONFIG_ANDROID_BINDERFS=y` and `CONFIG_ANDROID_BINDER_IPC=y`.

## Control Flow
Consumed by config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for mounting binderfs and exercising binder device ioctls.

## Risks
Runtime namespace and permission policy can still skip/fail tests despite config.

## Test Signals
Successful binderfs mount and binder-control access indicate config support is present.
