# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/rtase/Makefile

## Purpose

This Kbuild file wires the Realtek Automotive Switch Ethernet driver into the Linux kernel build. It declares that `CONFIG_RTASE` builds the `rtase` module or built-in object and that the module is composed from `rtase_main.o`.

## Important APIs, Types, And Functions

There are no C APIs or runtime functions in this file. Its important build variables are:

- `obj-$(CONFIG_RTASE) += rtase.o`, which lets Kbuild include the driver when the kernel configuration selects `CONFIG_RTASE`.
- `rtase-objs := rtase_main.o`, which tells Kbuild to link `rtase.o` from `rtase_main.o`.

The SPDX expression is dual `GPL-2.0 OR BSD-3-Clause`, matching the rtase driver header.

## Control Flow

Build control flow is entirely declarative. During kernel build, Kbuild expands `obj-y` or `obj-m` depending on whether `CONFIG_RTASE=y` or `CONFIG_RTASE=m`. If enabled, it compiles `rtase_main.c` into `rtase_main.o` and links it into `rtase.o`.

## State And Persistence

The file has no runtime state. Its persistent effect is build-graph state: enabling `CONFIG_RTASE` creates a `rtase` driver object from a single implementation file. Adding future split files would require extending `rtase-objs`.

## Dependencies And Integration Points

This file depends on the parent kernel build system and a Kconfig symbol named `CONFIG_RTASE` defined elsewhere in the Realtek driver tree. It integrates with module naming, modpost, dependency generation, and kernel install packaging through standard Kbuild semantics.

## Risks And Edge Cases

The main risk is build drift. If `rtase_main.c` is renamed, split, or supplemented with helper files, `rtase-objs` must be updated or the module will fail to link. If `CONFIG_RTASE` is missing or not selected by the parent directory Makefile/Kconfig, this file will be inert. License metadata should stay consistent across all rtase source files.

## Test Signals

Useful signals are `make M=drivers/net/ethernet/realtek/rtase`, a full kernel build with `CONFIG_RTASE=m` and `CONFIG_RTASE=y`, successful `modpost`, and confirming the resulting module/object contains the expected `rtase_main.o` symbols.
