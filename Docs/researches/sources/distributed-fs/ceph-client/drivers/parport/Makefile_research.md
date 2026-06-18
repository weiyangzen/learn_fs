# sources/distributed-fs/ceph-client/drivers/parport/Makefile

## Purpose
The Makefile maps parport Kconfig symbols to kernel objects and defines which compilation units form the core `parport` module.

## Important APIs, Types, and Functions
`parport-objs` always contains `share.o`, `ieee1284.o`, `ieee1284_ops.o`, and `procfs.o`. If `CONFIG_PARPORT_1284=y`, it adds `daisy.o` and `probe.o`. `obj-$(CONFIG_...)` lines bind config symbols to low-level driver objects such as `parport_pc.o`, `parport_cs.o`, `parport_amiga.o`, `parport_gsc.o`, and `parport_ip32.o`.

## Control Flow
kbuild evaluates the core object list, conditionally extends it for IEEE 1284 discovery/probe support, then includes low-level modules based on selected config symbols. The core can be built-in or modular via `CONFIG_PARPORT`.

## State and Persistence
This is build metadata only. Its main stateful effect is the composition of the `parport` module, especially whether daisy-chain and probe code is linked.

## Dependencies and Integration Points
It consumes symbols declared in `Kconfig` and integrates all C files in this subset with the kernel build. It also implies that `ieee1284.c` and `ieee1284_ops.c` are always part of core parport, while `daisy.c` is only present when `PARPORT_1284` is built into the core.

## Risks
Because `daisy.o` and `probe.o` are included only when `CONFIG_PARPORT_1284` equals `y`, a modular or disabled advanced-mode configuration must be checked against intended behavior. Missing an `obj-*` mapping would silently omit a platform driver even if Kconfig offers it.

## Test Signals
Build logs or `make V=1` should show the expected object list for each config. `modinfo` or built-in symbol inspection should show platform drivers only when their configs are selected.
