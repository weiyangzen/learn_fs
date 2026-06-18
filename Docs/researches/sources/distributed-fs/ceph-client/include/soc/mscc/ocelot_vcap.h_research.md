# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_vcap.h

Purpose: defines the public model for Ocelot VCAP programmable classification blocks ES0, IS1, and IS2. It describes hardware properties, TCAM update registers, key/action field IDs, typed match structures, action payloads, filter identity/statistics, private driver cookies, and filter management APIs.

Important APIs/types/functions: key exports are `struct vcap_props`, `struct vcap_field`, typed match structs such as `ocelot_vcap_key_vlan`, `ocelot_vcap_key_ipv4`, and `ocelot_vcap_key_ipv6`, `struct ocelot_vcap_action`, `struct ocelot_vcap_filter`, and APIs `ocelot_vcap_filter_add`, `ocelot_vcap_filter_del`, `ocelot_vcap_filter_replace`, and `ocelot_vcap_block_find_filter_by_id`.

Control flow: users allocate and populate `struct ocelot_vcap_filter`, choose a block/key/action, set cookie/offload identity, then add, replace, delete, or query stats through `ocelot_vcap.c`. The implementation packs fields using the property tables, writes cache rows, issues VCAP update commands, and maintains ordered filter lists.

State and persistence: software state is in per-block filter lists, cookies, TC offload IDs, stats, policer indices, and trap flags. Persistent hardware state is TCAM entries, masks, actions, counters, and optional policers until removed or reset.

Dependencies and integration: depends on `soc/mscc/ocelot.h`, Linux list/netlink types through includers, and VSC7514/Felix property tables. It integrates with tc flower, VLAN tag push/pop rules, PTP and MRP traps, mirroring, policing, DSA tag rules, and switchdev offload.

Risks: VCAP packing is bit-exact and priority/order-sensitive. Duplicate cookies, wrong key type, mismatched port masks, or bad action widths can shadow rules, leak traffic, mis-trap PTP/MRP packets, or corrupt counters. Test signals include tc flower add/delete/replace/stats, VLAN rewrite, PTP trap installation, MRP trap tests, policer resource cleanup, and hardware hit counters.
