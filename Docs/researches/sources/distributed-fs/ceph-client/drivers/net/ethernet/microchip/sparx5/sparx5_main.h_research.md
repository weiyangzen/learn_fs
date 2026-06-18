# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.h

## Purpose
`sparx5_main.h` is the central internal contract for the Sparx5 switch driver. It defines target IDs, port/VLAN/calendar/feature constants, frame DMA and PTP state, port and switch-wide runtime structures, match-data abstractions, subsystem prototypes, and inline register access helpers used across the driver.

The header is both a device model definition and a cross-file API surface. Most Sparx5 source files include it to access `struct sparx5`, `struct sparx5_port`, shared constants, hardware ops, and register read/write helpers.

## Important APIs, Types, And Functions
Target and configuration enums include `enum spx5_target_chiptype` for native Sparx5 and LAN969x part IDs, `enum sparx5_port_max_tags`, `enum sparx5_vlan_port_type`, `enum sparx5_cal_bw`, `enum sparx5_feature`, and `enum sparx5_core_clockfreq`.

Core constants define front and internal port counts (`SPX5_PORTS`, `SPX5_PORTS_ALL`), internal CPU/VD port indexes, PGID indexes, IFH length and rewrite/PDU encodings, MAC table pull delay, stats delay, priority count, buffer cell size, FDMA channel/DCB sizes, PTP PHC count, calendar dimensions, and PSFP/SDLB limits.

Important state types:

- `struct sparx5_calendar_data` stores DSM calendar calculation scratch arrays.
- `struct sparx5_rx`, `struct sparx5_tx_buf`, and `struct sparx5_tx` describe FDMA RX/TX rings, SKB/page ownership, DMA addresses, NAPI, counters, and transmit buffer state.
- `struct sparx5_port_config` stores per-port media, bandwidth, PHY mode, autoneg/pause, power, SerDes reset, and signal-detect settings.
- `struct sparx5_port` is the per-netdev private object with netdev, parent `sparx5`, OF/SerDes/phylink state, VLAN defaults, signal-detect state, injection timer, PTP TX tracking, mrouter flag, and TC template list.
- `struct sparx5_phc` and `struct sparx5_skb_cb` hold PTP clock and per-SKB timestamping metadata.
- `struct sparx5_mdb_entry`, `struct sparx5_mall_entry`, and mirror-related structs model multicast database and matchall mirror state.
- `struct sparx5_regs` points to generated register metadata arrays. `struct sparx5_consts` stores target-specific capacities and VCAP metadata. `struct sparx5_ops` stores target-specific callbacks for port classification, muxing, scheduling, PTP, calendar, and FDMA operations. `struct sparx5_main_io_resource` maps target IDs to resource offsets. `struct sparx5_match_data` bundles all per-compatible match data.
- `struct sparx5` is the top-level device state: platform device, `dev`, chip identity, feature bits, mapped target bases, ports, locks, statistics work, notifier blocks, bridge masks, VLAN masks, MAC/MDB lists, workqueues, frame I/O IRQs and FDMA state, PTP state and locks, VCAP control, PGID map, mirror entries, debugfs root, and match data.

The header declares subsystem APIs for switchdev notifiers, packet extraction/injection, FDMA, MAC table, VLAN/PGID, calendar, ethtool stats, optional DCB, netdev/IFH helpers, PTP, VCAP, pool allocation, port muxing/internal-port mapping, SDLB, policing, PSFP, QoS base-time adjustment, and mirror offload.

Inline helpers:

- `sparx5_clk_period()` maps core clock enum to picoseconds.
- `sparx5_is_baser()` identifies 5G/10G/25G BASE-R PHY interfaces.
- `spx5_offset()` computes a raw generated-register offset and warns on out-of-range target/group/register instances.
- `spx5_addr()` and `spx5_inst_addr()` compute MMIO addresses from generated register parameters.
- `spx5_rd()`, `spx5_wr()`, and `spx5_rmw()` perform normal read/write/read-modify-write operations against `sparx5->regs`.
- `spx5_inst_rd()`, `spx5_inst_wr()`, and `spx5_inst_rmw()` do the same for a supplied target base pointer.
- `spx5_inst_get()` returns a target-instance base pointer.
- `spx5_reg_get()` returns the computed MMIO address for a generated register.

## Control Flow
The header itself does not execute probe logic, but it shapes cross-module control flow. `sparx5_main.c` allocates and fills `struct sparx5`, maps target bases into `regs[]`, and invokes the subsystem init functions declared here. Packet, FDMA, PTP, VCAP, VLAN, MACT, QoS, and port modules then use the shared object and inline register helpers to operate on hardware.

Generated register macros expand into the long argument lists consumed by `spx5_rd()`, `spx5_wr()`, `spx5_rmw()`, and address helpers. This design lets call sites write compact register names such as `spx5_rd(sparx5, GCB_CHIP_ID)` while the inline functions still receive target ID, instance counts, group offsets, and register offsets.

The `sparx5_ops` callback table decouples common code from native Sparx5 versus LAN969x differences. Main probe loads `sparx5->data` from OF match data and downstream code calls through `data->ops` for port type checks, muxing, FDMA behavior, PTP IRQ handling, and calendar calculations.

## State And Persistence Behavior
All structures in this header represent volatile kernel state for a bound platform device; persistent hardware state lives in registers and switch memories addressed through `regs[]`. `struct sparx5` aggregates both long-lived resources and subsystem-owned transient state. Workqueues and locks inside it serialize asynchronous stats and MAC-table work. Bitmaps track bridge membership, forwarding, learning, and VLAN membership across `SPX5_PORTS`.

`struct sparx5_port` lives as netdev private data and points back to the parent `sparx5`. FDMA RX/TX state tracks DMA mappings and SKB/page ownership that must be released by FDMA teardown code. PTP fields include spinlocks and mutexes because timestamp ID allocation, PHC clock access, and interface state cross interrupt and process contexts. The PGID map is a fixed-size byte array used by multicast/flood resource allocation.

Register helpers are stateless, but they assume `sparx5->regs` entries have been populated before use and that the generated register metadata matches the active target. `WARN_ON()` checks catch invalid instance indexes in debug/test builds but do not prevent address calculation after warning.

## Dependencies And Integration Points
The header includes Linux PHY, phylink, netdevice, VLAN, bitmap, timestamping, PTP, hrtimer, debugfs, flow offload, and FDMA APIs, plus generated Sparx5 register definitions. It is included by most driver modules and is the dependency that ties subsystem prototypes together.

Integration with Linux networking is visible through `net_device`, NAPI, switchdev notifiers, ethtool ops, DCB ops, phylink MAC/PCS ops, flow offload mirror/matchall state, and bridge/VLAN state. Hardware integration is through register target IDs, target constants, FDMA channels, PTP PHC metadata, VCAP metadata, PSFP structures, policing structures, and SDLB scheduler parameters.

Because it declares many subsystem functions, changes to this header can affect compile dependencies across the whole driver. The generated register-call ABI also means edits to helper signatures must match generated macros in `sparx5_main_regs.h`.

## Risks
`struct sparx5` is large and shared widely, so field lifetime and locking rules are implicit. Misusing `sparx5->lock` versus subsystem locks can cause races around hardware access or software lists. The register helpers use long positional parameter lists; correctness depends on generated macros passing the right values in the right order. `WARN_ON()` detects but does not sanitize out-of-range indexes, so invalid input can still produce invalid MMIO addresses.

Several constants are target-specific but named globally, such as `SPX5_PORTS`, `SPX5_BUFFER_MEMORY`, and PGID table sizing; LAN969x support relies on `sparx5_consts` for runtime capacities in many places, but compile-time arrays and bitmaps remain sized for Sparx5 limits. The global `extern const struct phylink_*` and DCB/ethtool declarations require matching definitions in other modules. Optional DCB is compiled as a no-op inline when disabled, so callers must not depend on side effects in that configuration.

## Test Signals
Build coverage should include native Sparx5, LAN969x-enabled builds, and builds with and without `CONFIG_SPARX5_DCB`. Runtime tests should validate register helper addressing with representative target/group/register instances, port bitmaps at highest valid port indexes, FDMA RX/TX setup and teardown, PTP timestamp request/release paths, MAC/MDB list operations, PGID allocation near table limits, PSFP/SDLB resource boundaries, and phylink mode negotiation across SGMII/QSGMII/BASE-X/BASE-R/RGMII interfaces. Static analysis should focus on lock ordering, MMIO helper argument correctness, and array bounds in `struct sparx5` bitmaps and fixed-size tables.
