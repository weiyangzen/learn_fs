# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc830x_rdb.c

## Purpose
`mpc830x_rdb.c` registers Freescale MPC8308 RDB and derivative boards.

## Important APIs, Types, and Functions
`mpc830x_rdb_setup_arch()` calls common `mpc83xx_setup_arch()` and configures 831x-style USB via `mpc831x_usb_cfg()`. The compatible list includes `"MPC8308RDB"`, `"fsl,mpc8308rdb"`, and `"denx,mpc8308_p1m"`. The machine definition installs shared PCI, IPIC, restart, and time hooks.

## Control Flow, State, and Persistence
No local state is retained. Hardware mutations are delegated to common setup and USB helper code.

## Dependencies and Integration Points
It depends on FSL PCI/SOC, IPIC, UDBG, hidden `PPC_MPC831x` USB helper selection, and OF platform device declaration.

## Risks and Test Signals
Risks include USB helper matching MPC8308/8315 IMMR differences and generic PCI assumptions. Test signals are board matching, USB PHY/mux setup, PCI discovery, IPIC interrupts, and reboot.
