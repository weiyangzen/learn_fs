# sources/distributed-fs/ceph-client/drivers/mcb/Makefile

## Purpose
The Makefile wires MCB objects into Kbuild.

## Important APIs, Types, and Functions
It builds `mcb.o` from `mcb-core.o` and `mcb-parse.o` under `CONFIG_MCB`, and separately builds `mcb-pci.o` and `mcb-lpc.o` for their carrier configs.

## Control Flow, State, and Persistence
There is no runtime flow. Link composition matters because `mcb-core.o` exports the bus API and `mcb-parse.o` exports Chameleon parsing used by carriers.

## Dependencies and Integration Points
The file depends on the symbols declared in `drivers/mcb/Kconfig` and Kbuild's `obj-*`/`*-y` conventions. It is the build integration point for MCB namespace exports imported by carrier modules.

## Risks and Test Signals
Risks include omitting parser objects from the core module or changing module boundaries without adjusting namespace imports. Test signals are modular and built-in builds for each config combination and `modpost` namespace/export validation.
