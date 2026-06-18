# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_main.h

Purpose: central LAN966x driver header. It defines hardware constants, shared enums, device/port/FDMA/PTP/TC/QoS state structures, cross-module prototypes, register access helpers, and configuration stubs.

Important APIs and types: `struct lan966x` is the device-wide state container for MMIO targets, ports, bridge/VLAN/FDB/MDB/MAC/PTP/FDMA/VCAP/stats/debugfs state. `struct lan966x_port` stores netdev, chip port, VLAN/learning/mcast state, phylink/PCS/SerDes, PTP TX state, LAG state, TC state, and XDP state. `struct lan966x_rx`, `struct lan966x_tx`, and `struct lan966x_tx_dcb_buf` define FDMA rings and buffer ownership. `struct lan966x_phc` defines per-PHC PTP registration state. `struct lan966x_port_qos` and substructures define DCB QoS maps. Inline helpers `lan_addr`, `lan_rd`, `lan_wr`, and `lan_rmw` abstract generated register addressing.

Control flow and integration: all LAN966x modules include this header to share prototypes. Main calls subsystem init/deinit in probe/remove; TC modules call shaping/police/mirror/VCAP functions; switchdev calls FDB/MDB/LAG/VLAN/MAC helpers; data paths call IFH, PTP, FDMA, XDP, and stats helpers. `CONFIG_LAN966X_DCB` controls whether `lan966x_dcb_init` is real or a no-op.

State and persistence: the header defines all long-lived software state and many hardware index constants: physical ports, CPU port, PGIDs, queue counts, PHC count, FDMA channels, scheduler element indices, VCAP chain IDs, and IFH rewrite op/PDU types. These constants must remain synchronized with hardware and generated register definitions.

Dependencies and integration points: includes Linux netdevice, switchdev, phylink, PTP, page_pool, packet classifier/scheduler, XDP, shared FDMA and VCAP APIs, LAN966x registers, and IFH layout. It is the module boundary for files in this subset and related VLAN/PTP/TC/XDP sources.

Risks and test signals: structure or prototype changes ripple through almost every LAN966x source. Register helpers use `WARN_ON` bounds checks but still calculate addresses, so invalid generated macro arguments can write wrong MMIO. Test signals are compile coverage across Kconfig combinations, sparse/lockdep for shared state, and runtime coverage of every subsystem that stores fields in `struct lan966x` or `struct lan966x_port`.
