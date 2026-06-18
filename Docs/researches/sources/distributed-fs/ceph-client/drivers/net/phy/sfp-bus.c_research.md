# sources/distributed-fs/ceph-client/drivers/net/phy/sfp-bus.c

## Purpose
`sfp-bus.c` implements the rendezvous layer between an SFP socket driver and an upstream MAC/phylink user. It owns `struct sfp_bus`, parses module EEPROM identity into phylink capabilities, tracks references by firmware node, connects optional module PHY devices, and forwards module/link lifecycle events between socket and upstream callbacks.

## Important APIs, Types, And Functions
`struct sfp_bus` stores a `kref`, global list node, fwnode key, socket ops/device, upstream ops/private pointer, optional `phy_device`, registration/start flags, and `struct sfp_module_caps`. Public exports include `sfp_get_module_caps()`, `sfp_select_interface()`, `sfp_bus_find_fwnode()`, `sfp_bus_add_upstream()`, `sfp_bus_del_upstream()`, `sfp_get_name()`, `sfp_add_phy()`, `sfp_remove_phy()`, `sfp_link_up()`, `sfp_link_down()`, `sfp_module_insert()`, `sfp_module_remove()`, `sfp_module_start()`, `sfp_module_stop()`, `sfp_register_socket()`, and `sfp_unregister_socket()`.

## Control Flow
An upstream driver calls `sfp_bus_find_fwnode()` to resolve its `sfp` firmware reference, then `sfp_bus_add_upstream()` to attach operations. The socket driver calls `sfp_register_socket()` with `sfp_socket_ops`. If both sides are present, `sfp_register_bus()` calls upstream `link_down`, connects any already-probed module PHY, attaches the socket, starts it if the upstream is already started, and finally calls upstream `attach`. Removal reverses that through `sfp_unregister_bus()`.

EEPROM parsing starts in `sfp_module_insert()`, which calls `sfp_init_module()`. The parser decodes connector type into `caps.port`, determines whether a copper PHY may exist, derives link modes and possible host interfaces from base compliance, extended compliance, bitrate ranges, cable fields, and fibre-channel hints, then applies optional quirk support adjustments. `sfp_select_interface()` chooses the preferred `phy_interface_t` from requested link modes, prioritizing 25G, 10G, 5G, 2.5G, SGMII, 1000BASE-X, and 100BASE-X in that order.

## State And Persistence
The bus list is process-global and protected by `sfp_mutex`; bus attach/detach operations are serialized under RTNL. Bus objects persist until the last socket/upstream/reference user drops the `kref`. The current module capabilities are overwritten on each module insertion and remain readable through `sfp_get_module_caps()` while the module is present.

## Dependencies And Integration Points
The file integrates with firmware-node properties, phylink link-mode helpers, ethtool module EEPROM interfaces, RTNL locking, phylib `phy_device` attachment, and the local `sfp.h` socket ops contract. It is used by MAC/phylink users upstream and by `sfp.c` downstream.

## Risks And Edge Cases
Registration order matters; both socket-first and upstream-first paths must behave identically. `sfp_register_bus()` assumes `bus->upstream_ops` exists when it calls `attach`, so callers must only invoke it after upstream setup. Capability decoding is necessarily heuristic for modules with incomplete or incorrect EEPROM data. If a callback returns an error during registration, the code clears only the side that failed and relies on reference cleanup to avoid stale bus state.

## Test Signals
Exercise socket-first and upstream-first registration, upstream start before socket attach, module insertion/removal with and without onboard PHY, EEPROM capability parsing for optical, copper, passive DAC, 2.5G/5G/10G/25G cases, quirk capability overrides, `sfp_select_interface()` fallback warnings, and refcount cleanup after unregister paths.
