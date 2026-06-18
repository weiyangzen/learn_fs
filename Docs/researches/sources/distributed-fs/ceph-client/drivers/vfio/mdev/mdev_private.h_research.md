# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_private.h

## Purpose

This private header shares mdev bus, sysfs, and device lifecycle declarations among the mdev core source files.

## Important APIs, Types, and Functions

It declares `mdev_bus_type`, `mdev_device_groups`, type conversion macros, parent sysfs helpers, mdev sysfs helpers, and internal create/remove functions.

## Control Flow

There is no runtime flow. The declarations connect `mdev_core.c`, `mdev_driver.c`, and `mdev_sysfs.c`.

## State and Persistence Behavior

The header owns no state; it defines access to shared mdev structures.

## Dependencies and Integration Points

It depends on public mdev types and Linux container macros through included users. It is internal to the mdev module.

## Risks and Edge Cases

Macro correctness matters for kobject/attribute container conversions. Misuse would corrupt sysfs show/store context.

## Test Signals

Compile all mdev objects with sparse/build warnings and exercise every sysfs attribute path that uses the conversion macros.
