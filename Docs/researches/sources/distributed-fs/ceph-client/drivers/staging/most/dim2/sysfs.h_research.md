# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/sysfs.h

## Purpose
Declares a minimal MediaLB bus wrapper for DIM2 sysfs-related state.

## Important APIs, Types, And Functions
`struct medialb_bus` contains `struct kobject kobj_group`. In this source subset, `dim2.c` defines a `state` device attribute separately and includes this type in `struct dim2_hdm`.

## Control Flow
No functions or executable flow in the header.

## State And Persistence
Only declares a runtime kobject holder. No persistent storage.

## Dependencies And Integration Points
Depends on Linux kobject definitions and is included by `dim2.c`.

## Risks And Test Signals
The type is currently underused in the visible code, so future sysfs expansion must manage kobject initialization/lifetime carefully. Test signals are sysfs attribute registration/removal and probe/remove leak checks.
