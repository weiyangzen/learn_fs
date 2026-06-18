# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/efika.c

## Purpose
`efika.c` supports the bPlan Efika 5K2 MPC5200B computer, including RTAS-backed PCI config access, power management hooks, CPU info, and machine registration.

## Important APIs, Types, and Functions
When PCI is enabled, `rtas_read_config()` and `rtas_write_config()` implement `pci_ops` through RTAS tokens. `efika_pcisetup()` finds the root PCI node, allocates a controller, sets bus ranges, and processes OF ranges. `efika_probe()` identifies model `"EFIKA5K2"`, adjusts DMA mode constants, and sets `pm_power_off`. `efika_setup_arch()` initializes RTAS, maps common MPC52xx devices, and installs standby wakeup setup.

## Control Flow, State, and Persistence
The file persists machine hooks and global RTAS power-off/restart integration. PM state is delegated to common MPC52xx suspend with board wakeup GPIO configured on GPIO_WKUP_4.

## Dependencies and Integration Points
It depends on RTAS, OF root properties, MPC52xx common mapping, the generic MPC52xx PIC, and optional common PM code.

## Risks and Test Signals
Risks include RTAS token availability, root PCI node assumptions, DMA mode global changes, and wakeup wiring comments being board-specific. Test signals are Efika model detection, PCI config reads/writes through RTAS, `/proc/cpuinfo` fields, power-off/restart, and suspend/resume via the IRDA connector wake line.
