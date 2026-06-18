# sources/distributed-fs/ceph-client/net/bridge/br_stp.c

## Purpose
`br_stp.c` implements the core in-kernel IEEE 802.1D STP state machine. It selects root/designated ports, records received configuration, transitions ports between blocking/listening/learning/forwarding, handles topology-change propagation, and validates bridge STP timing and ageing-time configuration.

## Important APIs, types, and functions
- `br_set_state()` changes a port state, updates MST instance 0 when enabled, offloads STP state through switchdev, logs transitions, and updates STP xstats for kernel STP.
- `br_root_selection()`, `br_designated_port_selection()`, `br_configuration_update()`, and `br_port_state_selection()` are the core selection pipeline.
- `br_received_config_bpdu()` and `br_received_tcn_bpdu()` are BPDU receive entry points from `br_stp_bpdu.c`.
- `br_transmit_config()`, `br_transmit_tcn()`, and `br_config_bpdu_generation()` create outbound STP traffic through BPDU helpers.
- `br_topology_change_detection()` and `__br_set_topology_change()` manage topology-change flags and ageing-time reduction/restoration.
- `br_set_hello_time()`, `br_set_max_age()`, `br_set_forward_delay()`, `br_set_ageing_time()`, `__set_ageing_time()`, and `br_get_ageing_time()` implement user-facing timer configuration.

## Control flow
When topology or configuration changes, `br_configuration_update()` chooses the root port and designated ports, then `br_port_state_selection()` moves the selected ports forward or blocks them. Root selection compares designated root, total path cost, designated bridge, designated port, and local port ID. Root-blocked ports that would become root ports are held in listening and notified.

Received config BPDUs increment xstats, compare against current port information, record superior information, recompute bridge state, stop hello timers if the bridge lost root status, inherit root timing from the root port, generate updated config BPDUs, and process topology-change acknowledgements. TCN BPDUs on designated ports trigger topology-change detection and acknowledgement.

Port forwarding transition depends on STP mode: no STP or zero delay goes directly to forwarding; kernel STP enters listening; user STP enters learning. Topology changes reduce ageing time to twice forward delay during the change window and later restore configured bridge ageing time.

## State and persistence
STP state lives in `struct net_bridge` and `struct net_bridge_port`: root/designated IDs, root path cost, timers, topology flags, per-port designated info, states, pending flags, and xstats. It is volatile kernel state. Timers in `br_stp_timer.c` drive asynchronous progress.

## Dependencies and integration points
The file integrates with switchdev STP state/ageing-time offload, MST state, multicast port enable/disable, FDB ageing, rtnetlink notifications, carrier state, and BPDU send/receive helpers. User-facing control comes through netlink and sysfs setters.

## Risks and edge cases
Most functions require `br->lock`; missing locking would corrupt root/port selection. MRP-aware ports are excluded from STP state changes. Switchdev offload failures are logged but not always fatal. Ageing-time offload failure during topology change leaves software/hardware ageing mismatched. Root-block behavior intentionally prevents a superior port from taking over.

## Test signals
STP tests should simulate superior/inferior config BPDUs, TCN handling, root loss/regain, root-block ports, timer boundary validation, zero forward delay, kernel/user/no-STP modes, MST enabled state mirroring, switchdev offload errors, and ageing-time changes on topology events.
