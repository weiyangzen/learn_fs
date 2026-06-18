# sources/distributed-fs/ceph-client/drivers/vfio/mdev/Kconfig

## Purpose

This Kconfig file declares the mediated device core symbol used by VFIO and mdev-capable parent drivers.

## Important APIs, Types, and Functions

`VFIO_MDEV` is a tristate symbol with no prompt in this file, so it is selected by other features rather than normally chosen directly by users.

## Control Flow

When enabled, Kbuild builds the mdev core bus, sysfs, and driver-registration support.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

The symbol maps to `drivers/vfio/mdev/Makefile` and the exported mdev APIs used by parent/device drivers.

## Risks and Edge Cases

Because the option has no prompt, missing selects from consumers can silently omit mdev infrastructure.

## Test Signals

Build consumers that select mdev and ensure `mdev.o` is linked.
