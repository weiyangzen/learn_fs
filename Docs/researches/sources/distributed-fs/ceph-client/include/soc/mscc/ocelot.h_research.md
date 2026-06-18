# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot.h

Purpose: declares the Microsemi/Microchip Ocelot switch core register namespace, state structures, regmap helpers, packet I/O, switching, timestamping, QoS, devlink, phylink, VCAP, MRP, MAC Merge, and platform operations.

Important APIs and types: PGID constants/macros define L2 destination, aggregation, and source masks. `enum ocelot_target`, `enum ocelot_reg`, and `enum ocelot_regfield` enumerate switch targets, registers, counters, and regfields. `struct ocelot_ops` supplies platform callbacks for port mapping, reset, watermarks, PSFP, cut-through, TAS, and stats. State structs cover VCAP policers/blocks, bridge VLANs, PSFP lists, LAG FDBs, mirroring, MAC Merge state, timestamp stats, `struct ocelot_port`, and top-level `struct ocelot`. Macros wrap indexed regmap reads/writes/RMW and target reads/writes. Function declarations cover I/O, injection/extraction, PTP RX/TX timestamps, reset/init/deinit, DSA 802.1Q CPU ports, stats, VLAN/bridge/STP/FDB/MDB/LAG, hardware timestamping, policing/mirroring/flower, devlink shared buffers, SerDes/phylink, MAC table stream data, VCAP policers, MAC Merge, mqprio, optional MRP, and PLL init.

Control flow: platform drivers fill `struct ocelot`, initialize regmaps/regfields, reset/init ports, then switchdev/DSA/phylink/ethtool/TC callbacks manipulate bridge, VLAN, FDB, QoS, timestamp, and packet I/O state through these helpers.

State and persistence: runtime state is extensive: port objects, register maps, VLAN/trap/LAG/VCAP/PSFP lists, stats workqueues, locks, timestamp queues, PTP clock, MAC Merge state, FDMA, and hardware tables. It is rebuilt on probe, with no file persistence.

Dependencies and integration points: depends on networking, DSA, PTP, timestamping, VLAN, regmap, devlink, switchdev, phylink, TC flower/mqprio/taprio, and optional bridge MRP support.

Risks and test signals: risks include PGID forwarding-mask corruption, indexed register offset mistakes, lock-order issues among injection/extraction/stats/MAC table/PTP, stale FDB/VLAN/LAG state, timestamp skb leaks, optional MRP stubs returning `-EOPNOTSUPP`, and config drift across Ocelot/Felix variants. Test bridge/VLAN/FDB/MDB/LAG offload, DSA CPU tagging, PTP RX/TX, packet injection/extraction, ethtool stats, devlink SB, TC flower/PSFP/TAS/mqprio, MAC Merge, phylink speed modes, MRP enabled/disabled, and reset/deinit cleanup.
