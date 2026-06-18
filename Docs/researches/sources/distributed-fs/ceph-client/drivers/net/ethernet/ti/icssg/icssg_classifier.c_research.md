# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_classifier.c

## Purpose
`icssg_classifier.c` programs the ICSSG MII-G real-time classifier tables and gates used to accept, drop, or classify Ethernet frames for PRU Ethernet slices. It handles host/port MAC programming, default filtering, promiscuous mode, SR1 multicast filtering, source-address validation setup, and HSR/PRP PTP filter table programming.

## Important APIs, Types, and Functions
The file defines filter table constants for FT1 and FT3, classifier gate/select bitfields, slice-specific MII-G register offsets, and helpers that write FT1 destination-address slots, masks, config types, classifier AND/OR masks, selection modes, and gates. Exported functions are `icssg_class_set_host_mac_addr()`, `icssg_class_set_mac_addr()`, `icssg_class_disable()`, `icssg_class_default()`, `icssg_class_promiscuous_sr1()`, `icssg_class_add_mcast_sr1()`, `icssg_ft1_set_mac_addr()`, and `icssg_ft3_hsr_configurations()`.

## Control Flow and State
Classifier programming is direct regmap writes into per-slice offsets. `icssg_class_disable()` enables the L2 gateway, clears all classifier AND/OR matches, sets selection to OR, configures gates to allow filtered flow, disables all FT1 slots, clears their address/mask registers, and clears CFG2. `icssg_class_default()` starts from disabled state and enables broadcast plus PRU destination MAC matching, optionally multicast, for either five SR1 classifiers or one newer classifier. `icssg_class_promiscuous_sr1()` bypasses filters by setting RAW gates. `icssg_class_add_mcast_sr1()` reserves two FT1 slots for standard multicast prefixes, then adds netdev multicast addresses until slots are exhausted, falling back to allmulti.

## Dependencies and Integration Points
The file depends on `regmap`, Ethernet address helpers, `net_device` multicast iteration, and `icssg_prueth.h` for PRU mode/version data. It is invoked by ICSSG netdev setup, RX mode changes, and HSR/PRP offload configuration.

## Risks and Test Signals
The offset table is hardware-contract critical; wrong slice offsets silently program the wrong classifier. Slot exhaustion in SR1 multicast forces allmulti, so multicast-heavy workloads should be tested. HSR/PRP FT3 setup uses different EtherType offsets for PRP versus HSR and configures dedicated classifier indices, so mode switching needs validation. Test signals include unicast/broadcast/multicast acceptance, allmulti/promiscuous toggles, reserved multicast prefix handling, SAV FT1 MAC setup, SR1 versus non-SR1 default behavior, and PTP detection inside HSR/PRP tagged frames.
