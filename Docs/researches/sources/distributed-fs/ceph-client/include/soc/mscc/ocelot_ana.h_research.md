# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ana.h

Purpose: defines register bit masks, field encoders, field masks, and field extractors for the Microsemi/Microchip Ocelot ANA analyzer block. It covers ingress learning/aging, storm control, flooding, sFlow, VLAN and ISDX tables, stream/SFID/SG tables, per-port VLAN/QoS/VCAP/CPU-forwarding policy, PFC, OAM/IPT, DSCP, VCAP ranges, policers, and aggregation controls.

Important APIs/types/functions: this header exports macros only. Important groups include `ANA_TABLES_MACACCESS_*` plus `MACACCESS_CMD_*` for MAC table transactions, `ANA_TABLES_VLANACCESS_*` and command constants for VLAN table writes, `ANA_PORT_*` groups for per-port policy, `ANA_CPUQ_*` for exception queues, `ANA_POL_*` for ingress policers, and `*_RSZ`/`*_GSZ` constants used to index replicated registers.

Control flow: none is implemented in the header. Runtime flow is imposed by consumers that compose values with these macros, write index/data registers, then trigger hardware table commands and poll for completion. The table command constants define the key state transitions visible to software, such as learn, forget, age, get-next, init, read, and write.

State and persistence: all persistent state is hardware state in analyzer registers and SRAM/TCAM-style tables. Writes affect forwarding, learning, VLAN classification, CPU trapping, QoS classification, stream gates, and policer state until reset or later driver reconfiguration.

Dependencies and integration: depends on Linux `BIT()` and `GENMASK()` macro availability through includers. It is included by the common Ocelot Ethernet driver and DSA variants, including Felix/Seville support, where it integrates with bridge/VLAN, switchdev, tc flower, PTP trapping, MRP, policing, and statistics paths.

Risks: field widths are hardware ABI. Bad masks, shifts, port bitmaps, or command values can corrupt forwarding state, leak traffic between VLANs, drop control traffic, or stall table accesses. Replicated register size constants must match register-map definitions. Test signals are switchdev VLAN/bridge tests, tc flower offload tests, PTP trap tests, MRP tests, traffic flooding/learning checks, and hardware register readback on Ocelot/Felix boards.
