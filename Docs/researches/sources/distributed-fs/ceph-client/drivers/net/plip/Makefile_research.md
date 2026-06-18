# sources/distributed-fs/ceph-client/drivers/net/plip/Makefile

## Purpose
`Makefile` connects the PLIP driver object to the kernel build system. It builds `plip.o` when `CONFIG_PLIP` is enabled as built-in or module.

## Important APIs, Types, And Functions
The sole build rule is `obj-$(CONFIG_PLIP) += plip.o`.

## Control Flow
Kbuild expands `obj-y` for built-in PLIP or `obj-m` for module PLIP based on the Kconfig value. If `CONFIG_PLIP` is unset, no object is added.

## State And Persistence
The file holds no runtime state. Build state is determined entirely by `.config` and Kbuild.

## Dependencies And Integration Points
It integrates with `drivers/net/plip/Kconfig`, the kernel recursive Make system, and the `plip.c` source object in the same directory.

## Risks And Edge Cases
The rule assumes `plip.c` exists and produces a single `plip.o`. Any future split into helper objects would require updating this Makefile to keep module linkage complete.

## Test Signals
Build with `CONFIG_PLIP=y`, `CONFIG_PLIP=m`, and unset; verify built-in object inclusion and module generation.
