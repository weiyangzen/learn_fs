# sources/distributed-fs/ceph-client/net/openvswitch/conntrack.c

## Purpose

This file integrates Open vSwitch actions and flow keys with Linux netfilter conntrack, NAT, helpers, labels, marks, timeouts, event masks, and optional per-zone connection limits. It handles both control-plane parsing/serialization of OVS CT actions and packet-time execution of tracking and commit operations.

## Important APIs, Types, and Functions

The central action state is `struct ovs_conntrack_info`, containing helper, zone, template conntrack, commit/force/nat flags, family, event mask, mark/labels, timeout, timeout extension, and optional NAT range. Public functions include `ovs_ct_init()`, `ovs_ct_exit()`, `ovs_ct_verify()`, `ovs_ct_copy_action()`, `ovs_ct_action_to_attr()`, `ovs_ct_execute()`, `ovs_ct_clear()`, `ovs_ct_fill_key()`, `ovs_ct_put_key()`, and `ovs_ct_free_action()`.

Packet execution flows through `ovs_ct_execute()`, `__ovs_ct_lookup()`, `ovs_ct_lookup()`, and `ovs_ct_commit()`. Parsing uses `parse_ct()` and `parse_nat()`. Key update helpers include `ovs_ct_update_key()`, `__ovs_ct_update_key()`, `ovs_nat_update_key()`, and original tuple helpers. Optional conncount support defines `ovs_ct_limit_info`, zone limit hash manipulation, CT limit generic-netlink commands, and `dp_ct_limit_genl_family`.

## Control Flow

`ovs_ct_copy_action()` validates the packet family, parses nested CT attributes, allocates an nf_conntrack template for the selected zone, attaches timeout/helper state, stores the action in the flow action list, and marks templates confirmed when commit is requested. At packet time, `ovs_ct_execute()` pulls the skb to L3, trims network payload, defragments if needed, then calls lookup or commit. Lookup avoids duplicate conntrack work when cached state matches; otherwise it installs the zone template and calls `nf_conntrack_in()`.

If a connection exists, the code conditionally performs NAT, attaches helpers on commit, invokes helpers, makes TCP established tracking liberal, fills action extensions, and updates `sw_flow_key` CT fields. Commit applies event masks, mark, labels, conncount limits, and confirms the connection. NAT updates flow-key addresses/ports after translation.

## State and Persistence

Persistent state is in netfilter conntrack tables, conntrack labels/marks/timeouts, helper references, and optional per-net OVS CT limit tables. Per-action state is copied into flow actions and freed by `ovs_ct_free_action()`. Per-net initialization acquires connlabel capacity and initializes conncount data when enabled.

## Dependencies and Integration Points

The file depends heavily on netfilter conntrack core, zones, labels, helpers, timeouts, NAT, defrag, and conncount. It integrates with OVS flow netlink parsing, datapath per-net state, flow keys, and the action executor.

## Risks and Edge Cases

Conntrack state caching is subtle: stale `_nfct`, NAT direction inversion, forced commit, zone mismatch, helper mismatch, or timeout mismatch all force fresh tracking or deletion. Defragmentation can steal skbs, reported as `-EINPROGRESS`. Mark/label updates are allowed only with commit. NAT attributes require commit when specifying new source/destination ranges. Optional feature stubs and Kconfig combinations change supported keys/actions.

## Test Signals

Tests should cover CT lookup and commit for IPv4/IPv6, zones, invalid packets, fragments, NAT existing and new connections, helper attachment, timeout policy, event masks, mark/label masked writes, CT clear, original tuple key emission, forced commit, recirculation with cached CT state, conncount set/get/delete and limit exceed, plus configurations without NAT, labels, marks, timeouts, or conncount.
