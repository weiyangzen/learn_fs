# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/ntsync/config

## Purpose
Kernel config fragment enabling the Windows synchronization primitive driver tested by `ntsync.c`.

## Important APIs, Types, And Functions
Sets `CONFIG_WINESYNC=y`.

## Control Flow
Consumed by selftest config tooling; not executable.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for `/dev/ntsync` and the `linux/ntsync.h` ioctl UAPI exercised by the test.

## Risks
If the driver option name changes, the selftest may build but skip/fail at runtime because `/dev/ntsync` is absent.

## Test Signals
Presence of `/dev/ntsync` at runtime is the practical signal that this config requirement is satisfied.
