# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.c

## Purpose
`ksz_common.c` is the shared DSA switch driver core for Microchip KSZ8xxx, KSZ9xxx, LAN937x, and LAN9646 switches. It identifies switch silicon, publishes chip capability tables, binds common DSA callbacks, coordinates setup and teardown, and delegates chip-specific register layouts and features through `struct ksz_dev_ops`.

## Important APIs, Types, and Functions
The exported entry points are `ksz_switch_alloc()`, `ksz_switch_register()`, `ksz_switch_remove()`, `ksz_switch_shutdown()`, `ksz_switch_suspend()`, and `ksz_switch_resume()`. Shared helper exports include `ksz_r_mib_stats64()`, `ksz88xx_r_mib_stats64()`, `ksz_port_stp_state_set()`, `ksz_get_gbit()`, `ksz_get_xmii()`, `ksz_switch_macaddr_get()`, `ksz_switch_macaddr_put()`, `ksz_handle_wake_reason()`, and the global `ksz_switch_chips[]` table.

The central integration object is `ksz_switch_ops`, a `struct dsa_switch_ops` table that wires DSA callbacks for tagging, setup, phylink, MDIO, VLAN/FDB/MDB, mirroring, STP, bridge flags, stats, MTU, WoL, PTP timestamping, flower offload, traffic control, EEE, and DCB. Silicon-specific behavior is selected by `ksz_switch_chips[]`, which binds each supported chip ID to register tables, masks, shifts, port capabilities, MIB layouts, PTP capability, TX queue count, and one of the device operation tables for KSZ8463, KSZ88xx, KSZ87xx, KSZ9477-like, or LAN937x devices.

## Control Flow
Probe-facing code starts with `ksz_switch_alloc()`, which allocates `dsa_switch` and `ksz_device`, then bus-specific code calls `ksz_switch_register()`. Registration toggles optional reset GPIOs, handles KSZ8463 strap pins, initializes mutexes, detects the chip with `ksz_switch_detect()`, validates it against platform data or OF match data, runs chip-specific `init()`, allocates per-port state and MIB counters, parses port interface/RGMII delay/fiber/synclko/WoL device-tree properties, then calls `dsa_register_switch()`. After DSA setup, MIB polling is scheduled.

DSA setup flows through `ksz_setup()`: allocate VLAN cache, reset hardware, parse drive strength properties, create PCS for SGMII-capable parts, configure broadcast and multicast storm controls, configure CPU port and STP multicast address handling, initialize MIB counters, run chip-specific setup, enable global/port/PTP IRQ domains if an IRQ exists, register the PTP clock when supported, register the user or side MDIO bus, initialize DCB, and finally set the hardware start bit. Error paths unwind PTP and IRQ state.

Runtime port control flows through DSA callbacks. STP changes update per-port TX/RX/learning bits and call `ksz_update_port_member()` to recompute forwarding masks based on bridge membership, STP forwarding state, isolation, CPU port, and HSR ports. VLAN/FDB/MDB/mirror operations are thin dispatchers into `dev_ops`. Phylink callbacks advertise capabilities from chip data, program xMII mode and RGMII delays on external MAC ports, set speed/duplex/flow control on link-up, and trigger immediate MIB reads on link-down.

## State and Persistence
The driver state is held in `struct ksz_device` and per-port `struct ksz_port`: chip identity, regmaps, device-tree flags, mutexes, IRQ domains, VLAN cache, MIB counters, bridge/STP flags, PTP state, WoL flags, HSR state, and an optional refcounted global switch MAC address. Hardware register state is volatile and restored by setup; there is no filesystem persistence. MIB values are accumulated in memory and periodically refreshed by delayed work to avoid hardware counter overflow. WoL state can intentionally survive shutdown by avoiding reset when a port has PME enabled.

## Dependencies and Integration Points
The file integrates with Linux DSA, phylink, phylib/MDIO, regmap, OF, GPIO, pinctrl, irqdomain, ethtool stats/WoL/EEE, switchdev bridge/VLAN/FDB/MDB, tc flower/CBS/ETS, HSR offload, PTP hooks from `ksz_ptp.h`, DCB hooks from `ksz_dcb.h`, and chip-specific modules `ksz8`, `ksz9477`, and `lan937x`. Bus drivers such as `ksz_spi.c` provide regmaps and call the exported lifecycle functions.

## Risks and Edge Cases
Chip tables are dense and easy to regress: wrong port counts, CPU masks, register maps, MIB layouts, or interface capability arrays can break probe or expose invalid ports. `ksz_switch_detect()` has family-specific ID logic, including KSZ9893 SKU differentiation and LAN9646 special handling. MDIO setup validates `phy-handle` parents and PHY addresses; mismatched DT fails registration. IRQ setup nests global, port, PHY, and optional PTP domains and has multiple unwind points. Traffic-control code rejects unsupported ETS weights and requires all queues to be covered. WoL and HSR share a single global switch MAC address, so MAC changes are blocked while those features own it. `ksz_switch_macaddr_put()` assumes a valid refcounted address exists when called.

## Test Signals
Useful signals include successful probe for every compatible in `ksz_switch_chips[]`, DSA registration and teardown without leaks, correct tag protocol selection, MDIO child bus registration and IRQ mapping, STP forwarding/isolation behavior, VLAN/FDB/MDB/mirror operations, MIB counter rollover avoidance, phylink mode and RGMII delay programming, EEE advertisement only on allowed internal PHYs, CBS/ETS qdisc offload acceptance and rejection, WoL PME wake reason logging, HSR join/leave constraints, suspend/resume MIB work handling, and shutdown behavior with and without active WoL.
