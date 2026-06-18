# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Kconfig

## Purpose
`85xx/Kconfig` defines Freescale Book-E/e500 machine type support and the board options for the 85xx platform family.

## Important APIs, Types, and Functions
`FSL_SOC_BOOKE` depends on `PPC_E500`, selects FSL SOC support, UDBG 16550, MPIC, PCI capability, serial options, and CoreNet RCPM when appropriate. The visible board options include BSC9131 RDB, BSC9132 QDS, many MPC85xx/P10xx/P20xx boards, QEMU e500, CoreNet generic, and vendor boards. The listed BSC symbols select `DEFAULT_UIMAGE`.

## Control Flow, State, and Persistence
This file only affects build-time configuration and object inclusion.

## Dependencies and Integration Points
It integrates with `85xx/Makefile`, MPIC/FSL PCI/SOC support, SMP/PM helper selection, and 32-bit versus CoreNet board families.

## Risks and Test Signals
Risks include broad default selection for Book-E, board options missing required selects, and accidentally enabling incompatible board code. Test signals are defconfig coverage, menu dependency checks, and targeted BSC913x builds.
