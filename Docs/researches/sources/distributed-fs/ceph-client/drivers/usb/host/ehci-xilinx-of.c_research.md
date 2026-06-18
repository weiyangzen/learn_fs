# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-xilinx-of.c

## Purpose
Xilinx OpenFirmware EHCI host glue. It supports Xilinx XPS USB host cores with big-endian registers/descriptors, caps at offset `0x100`, optional full-speed support, and custom warning messages when unsupported non-high-speed devices cannot be enabled.

## Important APIs, types, and functions
`ehci_xilinx_port_handed_over()` reports likely LS/FS incompatibility when a port cannot be enabled. `ehci_xilinx_of_hc_driver` directly lists common EHCI callbacks and uses the custom `port_handed_over` hook. `ehci_hcd_xilinx_of_probe()` and remove manage OF resources and HCD lifecycle.

## Control flow
Probe resolves memory resource and IRQ from the device tree, creates the HCD, maps MMIO, marks both MMIO and descriptors big-endian, reads `xlnx,support-usb-fs` to set `hcd->has_tt`, points caps to `regs + 0x100`, and registers the HCD. Remove removes and releases the HCD.

## State and persistence behavior
State is in HCD/EHCI endian flags, `has_tt`, resource metadata, and mapped registers. Device-tree hardware configuration controls whether full-speed support is advertised for the HCD lifetime.

## Dependencies and integration points
Depends on OF address/IRQ/platform APIs, big-endian EHCI Kconfig support, USB HCD core, and shared EHCI callbacks. It matches `xlnx,xps-usb-host-1.00.a`.

## Risks and edge cases
The core always forces big-endian descriptor and register access; missing Kconfig support would break operation. IRQ mappings are not explicitly disposed on every failure/remove path. The warning hook can conflate power failures with unsupported speed, as noted in comments.

## Test signals
Probe on HS-only and FS-capable Xilinx cores, big-endian descriptor operation, LS/FS device insertion, high-speed enumeration, IRQ mapping failure, remove, and port enable failures are useful tests.
