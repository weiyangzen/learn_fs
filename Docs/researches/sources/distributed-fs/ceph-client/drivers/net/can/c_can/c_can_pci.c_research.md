<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c

Purpose: this file is the PCI bus wrapper for the shared Bosch C_CAN/D_CAN core. It supports STMicroelectronics STA2X11 and Intel EG20T/PCH CAN devices, handling PCI enablement, BAR mapping, register alignment selection, optional MSI, and PCH soft reset.

Important APIs, types, and functions: `struct c_can_pci_data` describes controller type, message object count, register alignment, clock frequency, BAR, and reset callback. Register accessors cover 16-bit aligned, 32-bit aligned, and 32-bit access variants. `c_can_pci_probe()` and `c_can_pci_remove()` manage PCI lifecycle. `c_can_pci_reset_pch()` pulses the PCH soft-reset register.

Control flow: probe enables the PCI device, requests regions, tries MSI and bus mastering, maps the configured BAR, allocates a C_CAN netdev, fills `struct c_can_priv` with device pointer, IRQ, MMIO base, clock frequency, register map, accessors, type, and RAMINIT/reset callback, then calls `register_c_can_dev()`. Remove unregisters the CAN netdev, frees the core device, unmaps the BAR, disables MSI, releases regions, and disables the PCI device.

State and persistence: PCI-specific state is static per-device data in the ID table plus mapped BAR address stored in `priv->base`. Runtime controller state is owned by the shared core after registration. MSI state and requested PCI regions persist while the device is bound.

Dependencies and integration points: it depends on the PCI subsystem, ST and Intel PCI IDs, `alloc_c_can_dev()`/`register_c_can_dev()` from the core, register maps from `c_can.h`, and SocketCAN via the shared core.

Risks: register alignment must match the device or all logical register access breaks. MSI enable is opportunistic; shared IRQ operation must still work. PCH reset writes into an offset in the mapped BAR and assumes that BAR layout. Frequency is hardcoded in ID data and must match hardware clocking.

Test signals: probe/remove both supported PCI IDs, verify MSI and non-MSI interrupt handling, check bit timing against 50 MHz and 52 MHz frequencies, run loopback TX/RX, exercise PCH reset on open, and validate cleanup on failures after enable, region request, BAR map, allocation, and registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_pci.c -->
