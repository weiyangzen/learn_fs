# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc836x_rdk.c

## Purpose
`mpc836x_rdk.c` registers the Freescale/Logic MPC8360 RDK board.

## Important APIs, Types, and Functions
`mpc836x_rdk_setup_arch()` calls common `mpc83xx_setup_arch()`. The machine definition uses compatible `"fsl,mpc8360rdk"` and common PCI, IPIC, restart, time, and UDBG hooks. `machine_device_initcall()` registers common OF platform devices.

## Control Flow, State, and Persistence
The file keeps no local state. Common setup creates IMMR BAT mapping and platform devices.

## Dependencies and Integration Points
It depends on FSL PCI/SOC support, IPIC, and OF platform population. Kconfig also selects GTM/LBC support for this board.

## Risks and Test Signals
Risks are low in this file but include reliance on common setup for all board needs and no explicit QUICC Engine pin initialization. Test signals are board-compatible matching, PCI enumeration, localbus/GTM devices, interrupt delivery, and restart.
