# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc5200_simple.c

## Purpose
`mpc5200_simple.c` provides a generic MPC5200 machine for boards whose firmware correctly configures GPIO, clocks, watchdog safety, and optional PCI.

## Important APIs, Types, and Functions
`mpc5200_simple_setup_arch()` maps common MPC52xx devices and configures XLB arbitration. The `board[]` compatible list covers several vendors and boards. `define_machine(mpc5200_simple_platform)` wires shared PCI, OF device population, PIC, IRQ, and restart hooks.

## Control Flow, State, and Persistence
The file itself persists no state. Runtime state is in shared MPC52xx common/PIC/PCI code.

## Dependencies and Integration Points
It integrates with OF compatible matching, `mpc52xx_map_common_devices()`, `mpc5200_setup_xlb_arbiter()`, generic PCI setup, and standard MPC52xx interrupt/restart handling.

## Risks and Test Signals
Risks are firmware assumptions: the generic platform will not correct board-specific muxing or clock mistakes. Test signals are boots for every compatible, watchdog reset only when DT marks a safe GPT, PCI enumeration when a PCI node exists, and device probing from OF population.
