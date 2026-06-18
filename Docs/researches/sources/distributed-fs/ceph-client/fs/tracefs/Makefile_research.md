# sources/distributed-fs/ceph-client/fs/tracefs/Makefile

## Purpose
This Makefile builds tracefs, the tracing virtual filesystem.

## Important APIs, Types, and Functions
It sets `tracefs-objs := inode.o` and adds `event_inode.o`, then includes `tracefs.o` in `obj-$(CONFIG_TRACING)`.

## Control Flow and State
There is no runtime logic. Build composition ensures both the base tracefs filesystem and dynamic eventfs implementation are linked when tracing is enabled.

## Persistence, Dependencies, and Integration
The build depends on `CONFIG_TRACING`. It integrates tracefs into the kernel as the filesystem used by ftrace and event tracing.

## Risks and Test Signals
Risk is build dependency drift if eventfs or inode symbols are split incorrectly. Build testing with `CONFIG_TRACING=y` and disabled tracing configurations verifies composition.
