# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Kconfig

## Purpose
`82xx/Kconfig` defines PowerQUICC II/82xx board support options.

## Important APIs, Types, and Functions
`PPC_82xx` depends on 32-bit Book3S and selects `FSL_SOC`. `EP8248E` selects CPM2, indirect PCI when PCI is enabled, PHYLIB, and MDIO bit-bang support. `MGCOGE` selects CPM2 and optional indirect PCI.

## Control Flow, State, and Persistence
The file has build-time effects only. It controls whether common PQ2 restart code and board-specific EP8248E/KM82xx files are compiled.

## Dependencies and Integration Points
It integrates with `82xx/Makefile`, CPM2 support, PHY/MDIO stacks, and board device-tree compatibles.

## Risks and Test Signals
Risks include missing selects for board-required subsystems and accidental builds without CPM2 or MDIO support. Test signals are configuration dependency checks and targeted builds for EP8248E and MGCOGE.
