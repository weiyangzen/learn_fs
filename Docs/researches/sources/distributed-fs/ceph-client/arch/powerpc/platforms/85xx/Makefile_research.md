# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Makefile

## Purpose
`85xx/Makefile` maps Freescale 85xx/e500 platform symbols to common, SMP/PM, and board-specific objects.

## Important APIs, Types, and Functions
It builds `common.o` unconditionally for the platform family, conditionally includes SMP and PM helpers, and maps board symbols to files including `bsc913x_rdb.o` and `bsc913x_qds.o`. It also composes I8259 helper objects for boards that need legacy interrupt support.

## Control Flow, State, and Persistence
This is build-time composition only. It determines which `define_machine()` records and common publish-device hooks are linked.

## Dependencies and Integration Points
It integrates Kconfig symbols with board files, common 85xx platform support, FSL PCI, MPIC, CoreNet, DIU, and vendor-specific support objects.

## Risks and Test Signals
Risks include missing helper objects for board-selected features and SMP/PM object conflicts with CoreNet RCPM. Test signals are all targeted board builds and link validation for common publish, SMP, PCI, and interrupt hooks.
