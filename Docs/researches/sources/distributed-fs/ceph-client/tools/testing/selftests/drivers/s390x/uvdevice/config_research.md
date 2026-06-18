# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/s390x/uvdevice/config

## Purpose
Kernel config fragment for the s390 Ultravisor UAPI device selftest.

## Important APIs, Types, And Functions
Sets `CONFIG_S390_UV_UAPI=y`.

## Control Flow
Consumed by selftest/kernel config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for `/dev/uv` and `UVIO_IOCTL_ATT` support tested by `test_uvdevice.c`.

## Risks
Only meaningful on s390x. Device access permissions can still cause runtime skip/failure even with config enabled.

## Test Signals
Runtime opening of `/dev/uv` is the practical signal that the config and platform support are present.
