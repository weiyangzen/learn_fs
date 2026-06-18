# sources/distributed-fs/ceph-client/net/dsa/port.c

## Purpose
This file implements operations on one DSA port: enabling/disabling, bridge and LAG join/leave, STP/MST state, VLAN filtering, FDB/MDB/VLAN/MRP operations, host address and VLAN programming, MTU propagation, phylink setup for shared ports, CPU-conduit migration, HSR offload hooks, and tag_8021q VLAN notifications.

## Important APIs, Types, And Functions
Public functions include `dsa_port_supports_hwtstamp()`, `dsa_port_set_state()`, `dsa_port_set_mst_state()`, enable/disable variants, `dsa_port_bridge_join()/leave()`, LAG helpers, `dsa_port_vlan_filtering()`, `dsa_port_skip_vlan_configuration()`, `dsa_port_ageing_time()`, bridge flag and MST helpers, FDB/MDB/VLAN host and user operations, MRP helpers, `dsa_port_change_conduit()`, `dsa_port_set_tag_protocol()`, `dsa_supports_eee()`, phylink create/destroy, shared-port link register/unregister, HSR join/leave, and tag_8021q VLAN add/del.

## Control Flow
Bridge join creates or references a `struct dsa_bridge`, broadcasts `DSA_NOTIFIER_BRIDGE_JOIN`, registers switchdev offload for the bridge port, and synchronizes bridge flags, STP state, VLAN filtering, and ageing time. Rollback unoffloads, flushes deferred work, broadcasts leave, and destroys the bridge object. Bridge leave unoffloads earlier through `pre_bridge_leave()`, destroys the bridge reference, broadcasts leave, resets standalone flags/STP/VLAN filtering, and preserves ageing time.

LAG join creates or references `struct dsa_lag`, notifies the tree, and if the LAG is already under a bridge, also joins that bridge. Leave unwinds bridge membership first, destroys the LAG reference, and notifies. VLAN filtering validates VLAN upper conflicts and global filtering constraints under RCU, calls driver `port_vlan_filtering`, updates standalone VLAN management, and synchronizes host flooding. FDB/MDB/VLAN operations package notifier payloads with the appropriate database identity: port, bridge, or LAG.

`dsa_port_change_conduit()` is the most complex path. It temporarily unoffloads bridge state, disables standalone VLAN filtering if needed, unsyncs host addresses, uninstalls live host UC, calls driver `port_change_conduit`, inherits MAC address if necessary, reinstalls addresses, restores VLANs, and rejoins the bridge. Multiple rewind labels attempt to restore the old conduit and old offload state on failure.

Phylink setup validates required OF link properties for CPU/DSA ports, allows legacy workarounds for known switches, creates phylink, and connects PHY/fixed links when described.

## State And Persistence
Port state lives in `struct dsa_port`: bridge and LAG references, STP state, learning, ageing time, VLAN filtering, CPU port affinity, hsr device, phylink pointer/config, tag receive callback, address/VLAN lists, and user netdev association. Bridge and LAG objects are refcounted across ports.

## Dependencies And Integration Points
This file bridges DSA with switchdev, bridge, VLAN, MST, LAG, HSR, MRP, phylink, OF, netlink extack, DSA notifiers in `switch.c`, tag_8021q, and user netdev helpers.

## Risks And Edge Cases
Global VLAN filtering constraints can reject bridge configurations spanning multiple bridges. VLAN uppers with overlapping bridge VIDs block enabling VLAN awareness. Conduit migration has many partial-failure paths and logs restoration failures but may still leave external state degraded if restoration fails. Shared-port OF validation has a legacy compatible whitelist; new hardware should not rely on missing link descriptions. Some driver callbacks are optional and return `-EOPNOTSUPP`, which higher layers intentionally ignore in selected cases.

## Test Signals
Tests should cover bridge join/leave rollback, LAG under bridge transitions, VLAN filtering with VLAN uppers and global filtering, FDB/MDB/VLAN notifier payloads, host address install/remove, conduit migration success and forced failures, phylink validation, HSR join/leave, MST fast ageing, MRP ops, and tag_8021q notifications.
