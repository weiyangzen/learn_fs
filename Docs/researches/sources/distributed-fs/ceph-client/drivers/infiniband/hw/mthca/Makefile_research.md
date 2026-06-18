# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Makefile

## Purpose
`Makefile` defines how the mthca driver is linked into the kernel build when `CONFIG_INFINIBAND_MTHCA` is selected.

## Important APIs, types, and functions
It adds `ib_mthca.o` under `obj-$(CONFIG_INFINIBAND_MTHCA)` and composes that object from core files including main, command, profile, reset, allocator, EQ, PD, CQ, MR, QP, AV, multicast, MAD, provider, memfree, UAR, SRQ, and catastrophic-error support.

## Control flow
Kbuild compiles the listed objects and links them into `ib_mthca.o`; module or built-in behavior follows the Kconfig tristate.

## State and persistence
The file has no runtime state. It persists the build graph for the driver and determines which source files must remain ABI-compatible at link time.

## Dependencies and integration points
It integrates all mthca implementation units and depends on Kbuild conventions and `CONFIG_INFINIBAND_MTHCA` from Kconfig.

## Risks
Omitting a source file would produce unresolved symbols or missing runtime functionality. Reordering has little effect for normal C objects, but adding new driver subsystems requires updating this list.

## Test signals
Run mthca compile builds as module and built-in, confirm all listed objects are compiled, and verify no unresolved symbols when feature options such as debug or MSI support vary.
