# sources/distributed-fs/ceph-client/drivers/tee/qcomtee/Makefile

## Purpose
The qcomtee Makefile defines the composite Qualcomm TEE driver object and its source components.

## Important APIs, Types, And Functions
`obj-$(CONFIG_QCOMTEE) += qcomtee.o` builds the driver when selected. `qcomtee-objs` includes async messaging, call handling, core driver registration, memory object support, primordial object support, shared memory, and user object handling.

## Control Flow And State
There is no runtime state. The object list shows that `async.c` is only one component of a larger object model with call, core, memory, primordial, SHM, and user-object modules.

## Dependencies And Integration Points
The file integrates with Kbuild composite object rules and the `CONFIG_QCOMTEE` symbol from Kconfig.

## Risks
All listed object files must compile together whenever QCOMTEE is selected; missing optional guards in any one file can break compile-test builds.

## Test Signals
Kernel builds with `CONFIG_QCOMTEE=m` and `CONFIG_QCOMTEE=y`, including `COMPILE_TEST`, are the primary signals.
