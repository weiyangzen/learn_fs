# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pci.c

## Purpose
`mpc52xx_pci.c` implements the MPC52xx PCI host bridge setup, config-space accessors, inbound/outbound windows, and resource fixups.

## Important APIs, Types, and Functions
`mpc52xx_setup_pci()` finds a matching PCI node and calls `mpc52xx_add_bridge()`. `mpc52xx_add_bridge()` allocates a PCI controller, sets bus ranges and ops, maps PCI registers, processes OF ranges, and calls `mpc52xx_pci_setup()`. Config accessors use CAR and cfg-data windows with optional original MPC5200 bugfix paths for type-1 cycles. `mpc52xx_pci_fixup_resources()` forces resource reassignment and hides the host bridge's fixed 1 GiB prefetch BAR.

## Control Flow, State, and Persistence
The PCI controller and mapped registers persist after setup. Hardware window registers are programmed for memory and I/O resources from DT.

## Dependencies and Integration Points
It depends on OF PCI nodes, `pci_process_bridge_OF_ranges()`, `pcibios_alloc_controller()`, PowerPC PCI hooks, and `CONFIG_PPC_MPC5200_BUGFIX`.

## Risks and Test Signals
Risks include incorrect endian/width config accesses, erratum path regressions, missing bus-range fallback assumptions, resource window translation errors, and intentionally not resetting external PCI bus. Test signals are PCI enumeration, config read/write on bus 0 and subordinate buses, resource reassignment, host-bridge BAR suppression, and device operation on original MPC5200.
