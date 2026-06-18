# sources/distributed-fs/ceph-client/include/net/bond_3ad.h

## Purpose
This header defines the IEEE 802.3ad/LACP mode contract for the bonding driver. It includes LACP and marker PDU wire formats, state-machine enums, per-bond and per-slave 802.3ad state records, statistics, and exported hooks used by common bonding code.

## Important APIs, Types, And Constants
- `PKT_TYPE_LACPDU`, `AD_TIMER_INTERVAL`, `AD_LACP_SLOW`, and `AD_LACP_FAST` define slow-protocol packet type and timer cadence.
- State enums model the 802.3ad receive, periodic, mux, transmit, and churn machines.
- `lacpdu_t` and `bond_marker_t` are packed wire records; `lacpdu_header_t` and `bond_marker_header_t` include Ethernet headers.
- `struct bond_3ad_stats` tracks LACPDU and marker receive/transmit/error counters with `atomic64_t`.
- `aggregator_t` represents a link aggregation group with actor/partner keys, system identifiers, active status, and linked ports.
- `port_t` represents a slave port with actor/partner admin and operational parameters, all state-machine state/timers, churn counters, RCU pointer to the aggregator, and prepared outbound LACPDU.
- `struct ad_bond_info` and `struct ad_slave_info` embed 802.3ad state into `struct bonding` and `struct slave`.
- Exported functions initialize/bind/unbind, run the state-machine work handler, trigger aggregator selection, handle speed/duplex and link changes, receive LACPDUs, update LACP settings, fill stats, and set carrier.

## Control Flow And State
Common bonding code initializes 802.3ad state with `bond_3ad_initialize()` when the bond enters mode 4. Each slave is bound with `bond_3ad_bind_slave()`, which populates the per-slave aggregator and port. Periodic work calls `bond_3ad_state_machine_handler()` at the LACP cadence to advance receive, periodic, mux, transmit, and churn machines, update timers, send LACPDUs or markers, and select an active aggregator. Packet receive paths call `bond_3ad_lacpdu_recv()` after slow-protocol classification. Link, speed, duplex, LACP rate, active/passive mode, and actor setting changes feed back into port state and may initiate aggregator reselection.

## State And Persistence Behavior
State is held in memory in `ad_bond_info` and `ad_slave_info`. The bond-level system identity and aggregator identifier persist while the bond exists. Per-port state includes actor/partner operational parameters, state-machine timers, churn counts, aggregator linkage, and the last composed LACPDU. RCU protects the port-to-aggregator pointer, while the bonding `mode_lock` is documented in `bonding.h` as protecting 3ad state against concurrent unbind and state-machine work. Statistics are atomic and exported through netlink/stat paths.

## Dependencies And Integration Points
The header depends on Ethernet, sk_buff, netdevice, byteorder, and common bonding declarations. It is included by `bonding.h` and implemented by `drivers/net/bonding/bond_3ad.c`. It integrates with bond options for LACP rate, active mode, actor system/priority/key, aggregator selection policy, carrier computation, and netlink stats.

## Risks
- Wire PDU structs are packed and protocol-specified; layout drift breaks interop with switches.
- State-machine timers are interdependent; wrong cadence or missed locking can cause churn, duplicate aggregation, or traffic blackholing.
- RCU aggregator pointer updates must coordinate with slave unbind and state-machine traversal.
- Speed/duplex changes affect aggregator eligibility and must be propagated promptly.
- Stats and LACP settings exposed through user interfaces must remain consistent with packet processing.

## Test Signals
- LACP tests should cover active/passive negotiation, fast/slow rates, partner default/expired/current transitions, link down/up, aggregator selection policies, and carrier/min-links behavior.
- Packet tests should validate LACPDU and marker parsing, illegal/unknown counters, and marker responses.
- Concurrency tests should stress slave removal while 3ad work and receive paths are active.
