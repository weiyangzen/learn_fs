# sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/usb4_port.c` creates the Linux device model representation for USB4 ports. It exposes sysfs attributes for link state and service-mode retimer access, binds USB4 port devices to Type-C connector devices through the component framework, supports firmware-node matching between USB3 and USB4 ports, and provides resume handling for ports left in offline mode. The source was read as a complete 366-line file for this report.

## Important APIs, Types, and Functions

Public entry points are `usb4_usb3_port_match`, `usb4_port_device_add`, `usb4_port_device_remove`, `usb4_port_device_resume`, and the exported `usb4_port_device_type`. Important local functions include `connector_bind`, `connector_unbind`, `link_show`, `offline_show`, `offline_store`, `rescan_store`, `service_attr_is_visible`, `usb4_port_offline`, and `usb4_port_online`.

Sysfs attributes are `link`, `offline`, and `rescan`. `link` is always visible and reports `usb4`, `tbt`, or `none`; `offline` and `rescan` are visible only when `usb4->can_offline` is set. The component operations create reciprocal sysfs links named `connector` and by USB4 port device name.

## Control Flow

`usb4_port_device_add` allocates `struct usb4_port`, initializes an embedded `struct device`, registers it below the owning switch device, adds the connector component, marks downstream ports wake-capable, and enables runtime PM with autosuspend. Removal deletes the component and unregisters the device.

`offline_store` parses a boolean, takes a runtime PM reference, locks the Thunderbolt domain, rejects offline mode when a remote router is connected, powers retimers through ACPI, asks the USB4 router sideband path to go offline, scans retimers, and records `usb4->offline`. Clearing offline mode brings the router online, powers retimers down, and removes discovered retimer devices. `rescan_store` requires the port to already be offline and then refreshes the retimer list.

`link_show` locks the domain and derives link type from upstream switch state, remote switch state, or attached XDomain state. `usb4_usb3_port_match` is designed for component matching: it follows the USB3 firmware node's `usb4-host-interface` reference, compares it against the NHI device fwnode, reads `usb4-port-number`, and compares it with `usb4_port_index`.

## State and Persistence Behavior

State is stored in the allocated `struct usb4_port` and linked from `struct tb_port->usb4`. The important persistent-in-memory fields are `port`, `offline`, `can_offline`, runtime PM state, wake capability, and the registered device lifetime. Hardware-side state changes happen through USB4 router offline/online sideband commands and ACPI retimer power calls. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Thunderbolt core structures in `tb.h`, runtime PM, the component framework, firmware-node property APIs, sysfs, ACPI retimer power helpers, retimer scan/remove helpers, USB4 sideband helpers from `usb4.c`, and Type-C connector components. It integrates with switch enumeration through `usb4_switch_add_ports`, with USB3 port binding through `usb4_usb3_port_match`, and with userspace through `/sys/bus/thunderbolt/devices/.../usb4_port*`.

## Risks and Edge Cases

Offline mode is intentionally limited to disconnected ports; forcing it while a remote switch exists returns `-EBUSY`. ACPI retimer power sequencing must stay balanced across offline failures and online transitions. `usb4_port_device_add` calls `device_unregister` after a component-add failure but still returns the allocated pointer, so callers rely on the current behavior and lifetime conventions. Sysfs operations must take the Thunderbolt domain lock because topology and XDomain pointers can change while userspace reads.

## Test Signals

Useful signals include creation/removal of `usb4_port*` devices during USB4 router enumeration; reciprocal connector sysfs links; `link` values for no device, USB4 router, TBT router, and XDomain connections; offline/rescan behavior with retimers present and absent; rejection of offline mode on connected ports; runtime PM autosuspend/resume preserving offline state; and firmware-node matching with USB3 component binding.
