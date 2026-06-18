# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/felix.h

## Purpose
This header defines the public internal interface between the shared Felix DSA library and chip-specific Ocelot-compatible front-end drivers. It declares supported port-mode bitmasks, `struct felix_info` hardware description, tag-protocol operation hooks, `struct felix` runtime state, and exported helper prototypes.

## Important APIs, Types, and Functions
- `ocelot_to_felix()` converts an embedded `struct ocelot *` back to `struct felix *`.
- `FELIX_MAC_QUIRKS` currently aliases `OCELOT_QUIRK_PCS_PERFORMS_RATE_ADAPTATION`.
- `OCELOT_PORT_MODE_*` bitmasks describe allowed PHY interface modes per port.
- `struct felix_info` is the chip profile consumed by `felix_register_switch()`. It contains resource tables, target names, regfields, register maps, Ocelot ops, port modes, MAC table and VCAP capacities, PTP caps, quirks, and optional callbacks for MDIO, tc, scheduler speed, MAC config, serdes, and IRQ setup.
- `struct felix_tag_proto_ops` abstracts setup/teardown and host-forwarding behavior for NPI versus `ocelot-8021q` tag protocols.
- `struct felix` stores DSA glue state and embeds the Ocelot switch-library object.
- Exported prototypes are `felix_register_switch()`, `felix_port_to_netdev()`, and `felix_netdev_to_port()`.

## Control Flow
Chip-specific drivers construct a static `felix_info` and call `felix_register_switch()`. The shared library uses the function pointers and resource descriptions from `felix_info` during DSA setup and later DSA callbacks. Tag-protocol operations are selected internally in `felix.c`.

## State and Persistence Behavior
The header defines runtime state but does not persist it. `struct felix` is devm-allocated during probe and removed with the device. Its `tag_proto`, `tag_proto_ops`, and host flood masks are mutable runtime state. `switch_base` is used for hardcoded resource offsets, while `pcs` and `imdio` are optional runtime resources owned by chip-specific MDIO setup.

## Dependencies and Integration Points
The types reference DSA, Ocelot switch-library structures, phylink, PTP caps, VCAP props, Linux resources, device tree nodes, net devices, tc setup types, and chip-specific register maps. This header is included by `felix.c`, `felix_vsc9959.c`, `ocelot_ext.c`, and the Seville front end.

## Risks and Edge Cases
- `resource_names` must have `TARGET_MAX` elements because it is indexed directly by target enum.
- `port_modes` must cover all `num_ports`, or device-tree PHY validation can read invalid data.
- Optional callbacks must be null-checked by the shared library before use; new callbacks should follow that pattern.
- `quirk_no_xtr_irq` changes timestamp trap behavior and must only be set for hardware where the extraction interrupt is truly unavailable.
- The `struct felix` embedded `struct ocelot` means lifetime and pointer conversion assumptions are tightly coupled.

## Test Signals
Compile coverage should include all chip-specific users of `struct felix_info`. Runtime validation should confirm that each front end supplies complete resource names/maps, valid per-port modes, correct optional callbacks, and matching PTP/IRQ capabilities. Static analysis should flag unguarded optional callback dereferences.
