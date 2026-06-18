# sources/distributed-fs/ceph-client/drivers/usb/typec/port-mapper.c

## Purpose

`port-mapper.c` links ACPI-described USB and USB4 ports with a Type-C connector using the component framework. It lets devices sharing the connector's ACPI physical location data bind as components of the Type-C port.

## Important APIs, Types, and Functions

`typec_link_ports()` scans ACPI devices for matching `_PLD` CRCs and builds a `component_match` list. `typec_unlink_ports()` removes the component master. `typec_aggregate_bind()` and `typec_aggregate_unbind()` call `component_bind_all()` and `component_unbind_all()` with the connector object. `typec_port_match()` compares ACPI companion devices and optionally adds a USB4 host-interface match using `usb4_usb3_port_match()`.

## Control Flow

Linking exits early for non-ACPI ports. For ACPI ports, it walks all ACPI devices, skips the connector's own companion, adds devices whose `_PLD` CRC matches, and adds USB4 matches when the matching fwnode advertises `usb4-host-interface`. If any match exists, the Type-C port becomes a component master. Unlink removes the master only for ACPI-backed ports.

## State and Persistence Behavior

The file stores no long-lived global state. Component framework registrations persist until unlink and bind/unbind the connector's `port->con` aggregate as matched devices appear or disappear.

## Dependencies and Integration Points

Dependencies are ACPI device enumeration, firmware nodes, component framework, Thunderbolt/USB4 matching, USB core, and Type-C class internals from `class.h`. It is a firmware topology bridge between Type-C connectors and USB/USB4 port devices.

## Risks and Test Signals

Risks include `_PLD` CRC collisions, the documented limitation that a connector can have only one component master, incorrect assumptions about USB4 fwnode properties, and no work on non-ACPI systems. Test signals include ACPI systems with shared `_PLD`, USB3 port matching, USB4 host-interface links, component bind/unbind order, and unlink on connector teardown.
