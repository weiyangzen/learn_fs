# sources/distributed-fs/ceph-client/drivers/vfio/mdev/Makefile

## Purpose

This Makefile builds the mediated device core module.

## Important APIs, Types, and Functions

`mdev-y` is composed from `mdev_core.o`, `mdev_sysfs.o`, and `mdev_driver.o`; `obj-$(CONFIG_VFIO_MDEV) += mdev.o` enables the aggregate object.

## Control Flow

Kbuild links the core lifecycle, sysfs, and bus/driver files into one module or built-in object.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies and Integration Points

The object list is the build contract for the mdev core exported APIs and bus type.

## Risks and Edge Cases

Dropping one object breaks exported helper resolution or mdev sysfs behavior.

## Test Signals

Build `CONFIG_VFIO_MDEV=y` and `m`, and verify mdev parent registration and driver registration link.
