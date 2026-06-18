# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/config

## Purpose
This config fragment requests the ublk kernel driver for the ublk selftests.

## Important APIs, Types, and Functions
It contains `CONFIG_BLK_DEV_UBLK=m`.

## Control Flow
No runtime control flow exists. The fragment is consumed by kselftest config tooling.

## State and Persistence
It does not mutate state.

## Dependencies and Integration Points
The shell tests call `modprobe ublk_drv`; this config declares the needed driver as a module.

## Risks
If the driver is built out or absent, most ublk tests skip or fail due to missing `/dev/ublk-control`.

## Test Signals
The signal is configuration intent for kernel test environments.
