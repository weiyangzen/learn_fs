# sources/distributed-fs/ceph-client/drivers/thunderbolt/acpi.c

## Purpose
`acpi.c` provides ACPI integration for Thunderbolt/USB4: runtime PM device links for tunneled ports, native-control policy checks, retimer power control through _DSM, and ACPI companion binding for routers and USB4 ports.

## Important APIs, Types, and Functions
Key APIs are `tb_acpi_add_links`, `tb_acpi_is_native`, `tb_acpi_may_tunnel_usb3`, `tb_acpi_may_tunnel_dp`, `tb_acpi_may_tunnel_pcie`, `tb_acpi_is_xdomain_allowed`, `tb_acpi_power_on_retimers`, `tb_acpi_power_off_retimers`, `tb_acpi_init`, and `tb_acpi_exit`. Internal helpers walk ACPI namespace, evaluate retimer DSM functions, and find companions.

## Control Flow
`tb_acpi_add_links` walks ACPI devices looking for `usb4-host-interface` references to the NHI, then creates PM runtime device links from PCIe root/downstream ports to the NHI. Policy helpers read global OSC native USB4 control bits. Retimer power checks whether the USB4 port supports offline mode, queries current DSM online state, and calls the set-online DSM when a transition is required. ACPI bus callbacks match Thunderbolt switches and USB4 port devices and locate companions by the documented NHI/host-router/downstream-port/device-router hierarchy.

## State and Persistence Behavior
Device links are managed by the driver core with autoremove flags. `usb4->can_offline` is set during ACPI setup when the retimer DSM is available. No file-backed persistence exists.

## Dependencies and Integration Points
It depends on ACPI, PM runtime, PCIe port type checks, Thunderbolt core types, USB4 port devices, and platform OSC variables.

## Risks and Edge Cases
DSM return values distinguish powered, busy, and error states; misinterpreting them can break retimer discovery. Device-link creation must keep NHI active long enough to establish supplier/consumer ordering. Companion lookup assumes ACPI topology conventions.

## Test Signals
ACPI namespace tests for NHI references, runtime PM ordering with tunneled PCIe ports, native-control policy checks under different OSC bits, retimer DSM success/busy/failure paths, and ACPI companion binding for host/device routers and ports.
