# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.c

## Purpose
`mpc5121_ads.c` registers the Freescale MPC5121 ADS board machine description and wires board-specific early setup, PCI discovery, interrupt initialization, restart, and common MPC512x initialization.

## Important APIs, Types, and Functions
`mpc5121_ads_setup_arch()` maps CPLD registers early and calls `mpc512x_setup_arch()`. `mpc5121_ads_setup_pci()` scans `"fsl,mpc5121-pci"` nodes and adds MPC83xx-style PCI bridges when PCI is enabled. `mpc5121_ads_init_IRQ()` initializes the MPC512x IPIC and cascaded CPLD PIC. `mpc5121_ads_probe()` calls `mpc512x_init_early()` before the flattened tree is fully available.

## Control Flow, State, and Persistence
The file itself persists no state. It sequences persistent mappings owned by shared MPC512x code and `mpc5121_ads_cpld.c`, then stores board hooks in `define_machine(mpc5121_ads)`.

## Dependencies and Integration Points
It depends on `mpc512x.h`, `mpc5121_ads.h`, IPIC, OF compatible `"fsl,mpc5121ads"`, and FSL PCI bridge support. It is the integration point between common SoC setup and ADS-only CPLD interrupt routing.

## Risks and Test Signals
Risks are mostly ordering-sensitive: CPLD mapping must happen before CPLD IRQ setup, PCI is initialized before the common clock provider is available, and probe returns true after early setup. Tests are ADS boot, PCI enumeration, CPLD interrupt delivery, serial console continuity, and restart behavior.
