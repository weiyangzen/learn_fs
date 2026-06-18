# File Research: sources/block-storage/parted/libparted/tests/zerolen.c

## Purpose

`zerolen.c` tests that libparted can probe a device reported as zero length without raising an exception.

## Main Responsibilities

- Accepts a device path argument.
- Sets `PARTED_TEST_DEVICE_LENGTH=0`.
- Installs the exception-aborting test handler.
- Calls `ped_device_get()` on the provided path.
- Destroys the device if it was returned.

## Behavior Under Test

The test is paired with `t2100-zerolen.sh`, which creates a device-mapper device and invokes this binary. Any unexpected libparted exception fails the test.
