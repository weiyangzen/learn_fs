# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_3ad.c

## Purpose
`bond_3ad.c` implements IEEE 802.3ad/LACP mode for the bonding driver. It maintains actor/partner port state, sends and receives LACPDU and marker frames, groups ports into aggregators, selects the active aggregator according to policy, drives the LACP receive/periodic/mux/transmit/churn state machines, reacts to link and speed changes, manages carrier state, and exposes LACP statistics.

## Important APIs, Types, and Functions
- State-machine helpers include `ad_rx_machine()`, `ad_periodic_machine()`, `ad_mux_machine()`, `ad_tx_machine()`, `ad_churn_machine()`, `ad_port_selection_logic()`, and `ad_agg_selection_logic()`.
- Packet functions `ad_lacpdu_send()`, `ad_marker_send()`, `bond_3ad_lacpdu_recv()`, and `bond_3ad_rx_indication()` implement LACP/marker frame I/O.
- Aggregator and port lifecycle functions include `bond_3ad_initialize()`, `bond_3ad_bind_slave()`, `bond_3ad_unbind_slave()`, `ad_initialize_port()`, `ad_initialize_agg()`, and `ad_clear_agg()`.
- Change handlers include `bond_3ad_adapter_speed_duplex_changed()`, `bond_3ad_handle_link_change()`, `bond_3ad_update_ad_actor_settings()`, `bond_3ad_update_lacp_rate()`, and `bond_3ad_update_lacp_active()`.
- Status/stat APIs include `bond_3ad_set_carrier()`, `bond_3ad_get_active_agg_info()`, `bond_3ad_stats_size()`, and `bond_3ad_stats_fill()`.

## Control Flow
Bond initialization records actor system priority/MAC and starts an aggregator selection timer. When a slave is bound, its port is initialized with actor state, keys derived from user key, speed, and duplex, then disabled until state machines enable it. The delayed work handler `bond_3ad_state_machine_handler()` runs every `ad_delta_in_ticks`, advances the aggregator selection timer, optionally selects the active aggregator, then for each slave runs RX timeout processing, periodic LACP scheduling, port selection, mux transitions, LACP transmit, and churn detection. If mux or aggregator selection changed usable slaves, it rearms slave-array work and may notify RTNL.

Receive paths consume only LACP destination multicast frames with protocol `PKT_TYPE_LACPDU`. LACPDU payloads enter `ad_rx_machine()` under `mode_lock`; marker frames are answered or counted. The RX machine records partner state, detects loopback, manages current/expired/defaulted states, and updates `AD_PORT_MATCHED`, `AD_PORT_SELECTED`, and synchronization. The mux machine transitions ports between detached, waiting, attached, collecting, distributing, and collecting/distributing states, setting bonding slave active/inactive flags. Aggregator selection chooses a best active LAG based on individual/partner status and `ad_select` policy (`stable`, `bandwidth`, `count`, or `prio`).

## State and Persistence
State is stored in `BOND_AD_INFO(bond)` and `SLAVE_AD_INFO(slave)`: system identity, aggregator identifiers, timers, stats, per-port state bits, actor/partner params, selected aggregator pointer, LACPDU template, churn counters, and active flags. Timers are software counters in delayed work ticks. There is no disk persistence; state is rebuilt from bond parameters and slave link characteristics.

## Dependencies and Integration Points
The file depends on bonding internals (`struct bonding`, `struct slave`, mode locks, slave-array updates, carrier helpers), `net/bond_3ad.h` protocol structures, netdev/skb APIs, ethtool speed/duplex values, RCU iteration over slaves, RTNL notifications, and netlink stat filling. It integrates with `bond_main.c` receive handling, mode initialization, link monitoring, sysfs/netlink option updates, and transmit eligibility through slave flags.

## Risks
The implementation is concurrency-sensitive: delayed work, receive handler, link changes, and unbind paths coordinate with `mode_lock`, RCU, and RTNL. Aggregator selection assumes it is called with the first aggregator; a FIXME documents that this API shape is fragile. Incorrect speed/duplex reporting can alter actor keys and restart LACP. Loopback detection disables useful partner updates by returning early. Marker response support is intentionally minimal. Carrier depends on active aggregator and `min_links`, so stale aggregator state can affect link reporting.

## Test Signals
Strong tests include LACPDU TX/RX counters, loopback frame rejection, marker response behavior, aggregator formation with matching actor/partner keys, active aggregator selection under all `ad_select` policies, `min_links` carrier behavior, link up/down and speed/duplex transitions, lacp rate/active option updates, slave bind/unbind while traffic is running, churn counters after synchronization failure, netlink stats encoding, and switch interoperability with active and passive LACP peers.
