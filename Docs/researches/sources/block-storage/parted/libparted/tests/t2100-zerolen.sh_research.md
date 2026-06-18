# File Research: sources/block-storage/parted/libparted/tests/t2100-zerolen.sh

## Purpose

`t2100-zerolen.sh` sets up a Linux device-mapper test environment and runs the zero-length probing test.

## Main Responsibilities

- Sources `tests/init.sh` and `tests/t-lib-helpers.sh`.
- Requires root privileges.
- Requires device-mapper support.
- Skips unless running on Linux.
- Skips unless `ENABLE_DEVICE_MAPPER=yes`.
- Creates a loop device over a temporary file.
- Creates a linear device-mapper target named `plinear-$$`.
- Waits for `/dev/mapper/<name>` to appear.
- Runs `zerolen /dev/mapper/<name>`.
- Cleans up dmsetup and loop devices, retrying dm removal to tolerate udev races.

## Behavior Under Test

The wrapper supplies a real `/dev/mapper` path so `zerolen.c` can verify that probing a device reported as zero length does not raise an exception.
