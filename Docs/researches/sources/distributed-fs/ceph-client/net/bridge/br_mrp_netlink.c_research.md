<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c

Purpose: provides rtnetlink parsing, validation, reporting, and user notification glue for bridge MRP. It translates nested `IFLA_BRIDGE_MRP_*` attributes into typed bridge MRP operations, fills link information for configured MRP instances, and toggles per-port continuity-loss flags that are reported through bridge link notifications.

Important APIs, types, and functions:

- `br_mrp_parse()` is the main setter/deleter entry point called from bridge link handling.
- `br_mrp_fill_info()` emits configured MRP instances into `IFLA_BRIDGE_MRP` nested attributes.
- Notification helpers `br_mrp_ring_port_open()` and `br_mrp_in_port_open()` update port flags and send `RTM_NEWLINK`.
- Parser helpers cover instance add/delete, port state, port role, ring state, ring role, ring test start, interconnect state, interconnect role, and interconnect test start.
- Netlink policies define required nested attribute types and reject unspecified attributes.

Core control flow:

- `br_mrp_parse()` first corrects the bridge pointer when called for a port and rejects MRP configuration if STP is enabled. It parses the top-level nested MRP attributes and processes each present sub-command in a fixed order, returning immediately on the first error.
- Instance parsing requires ring ID plus primary and secondary ifindices, defaults priority to `MRP_DEFAULT_PRIO` if absent, and calls `br_mrp_add()` for `RTM_SETLINK` or `br_mrp_del()` otherwise.
- Port-level parsers require a valid port pointer from the caller and pass role/state values to `br_mrp_set_port_state()` or `br_mrp_set_port_role()`.
- Ring and interconnect parsers build small typed structures, require IDs and state/role fields, then call the matching runtime functions in `br_mrp.c`.
- Start-test parsers enforce minimum interval of 1 through netlink policy, require interval, max-miss, and period fields, default monitor to false for ring tests, and call the software/hardware start functions.
- `br_mrp_fill_info()` iterates `br->mrp_list` under RCU assumptions and emits ring ID, participating ifindices, priority, ring state/role, test interval/max-miss/monitor, interconnect state/role, and interconnect test parameters for each instance.
- `br_mrp_ring_port_open()` and `br_mrp_in_port_open()` look up the bridge port by device, set or clear `BR_MRP_LOST_CONT` or `BR_MRP_LOST_IN_CONT`, and notify link listeners.

State and persistence behavior:

- This file owns no independent durable state. It mutates `struct br_mrp` and `struct net_bridge_port` state through runtime APIs and port flags.
- Netlink extack messages are the main diagnostics for missing attributes, STP conflicts, and invalid parser inputs.
- MRP info dumps reflect current in-kernel runtime fields; they are not reconstructed from userspace configuration.

Dependencies and integration points:

- Relies on UAPI definitions in `uapi/linux/mrp_bridge.h`, generic netlink/rtnetlink nested attribute helpers, bridge runtime functions in `br_mrp.c`, bridge port lookup from `br_private.h`, and link notifications through `br_ifinfo_notify()`.
- The parser is part of bridge link configuration alongside VLAN, STP, and other bridge attributes.
- MRP cannot coexist with STP according to this control-plane guard.

Risks and edge cases:

- `br_mrp_parse()` can receive either bridge-level or port-level requests. Some attributes require a port pointer; callers must only provide them in the correct context.
- Top-level processing is sequential and not transactional across multiple nested attributes. If a later attribute fails, earlier changes remain applied.
- Attribute presence validation is manual. Missing required fields produce extack errors; unexpected command combinations can still depend on lower-level runtime validation.
- `br_mrp_fill_info()` must size skb space correctly in its caller; failure paths cancel the right nested attributes to avoid malformed netlink messages.
- Continuity notification helpers use `br_port_get_rcu()` and mutate flags; callers should already be in an RCU-safe context or otherwise guarantee object lifetime.

Test signals:

- Configure every MRP nested attribute through `ip link`/rtnetlink and verify success, extack strings for missing fields, and error paths for STP-enabled bridges.
- Dump link info after each operation and confirm ring IDs, ifindices, roles, states, intervals, max-miss values, and monitor flags.
- Send multi-attribute requests where a later operation fails and verify the non-transactional resulting state.
- Trigger ring and interconnect open/closed notifications and observe `BR_MRP_LOST_CONT` / `BR_MRP_LOST_IN_CONT` reflected in link events.
- Test port-context misuse, invalid ifindices, duplicate IDs, and disabled interconnect role handling through lower runtime validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_netlink.c -->
