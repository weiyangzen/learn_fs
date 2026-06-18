## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_tc_flower.c

Purpose: this file translates tc flower filters into LAN966x VCAP rules. It parses supported flow dissector keys, validates action sequences and chain transitions, selects VCAP action sets, installs rules, deletes rules by cookie, and reports hardware counters.

Important APIs and functions: `lan966x_tc_flower()` dispatches replace/destroy/stats. `lan966x_tc_flower_add()` allocates a VCAP rule for the tc chain, parses dissectors, adds chain-link target keys/actions, maps tc actions, validates the rule, and commits it. `lan966x_tc_flower_use_dissectors()` iterates the handler table for Ethernet, IPv4/IPv6, control/fragment, ports, basic proto, VLAN/CVLAN, TCP, ARP, and IP keys. `lan966x_tc_flower_action_check()` enforces action uniqueness, hardware stats support, legal goto placement, and trap/pass conflicts.

Control flow: basic parsing records L3/L4 protocol and emits VCAP keys differently for IS1, IS2, and ES0. IS1 has special handling for ETYPE length/SNAP/IP4 indicators and TCP/UDP hints; IS2 supports additional known ethertypes. VLAN keys use IS1-specific `VID0/PCP0` fields or classified VLAN fields in other VCAPs. Control keys map fragment flags to `L3_FRAGMENT` and `L3_FRAG_OFS_GT0`. Actions support trap only in IS2, goto chain links from IS1 to IS2 via PAG or IS1 to ES0 via ISDX, and VLAN pop only in ES0 by forcing untagged output.

State and persistence: software state is VCAP rule metadata: cookie, priority, chain index, selected actionset, keys, actions, counters, and generated rule ID. Persistent hardware state resides in the VCAP tables through the shared VCAP API. Stats are read by cookie and reported as immediate hardware packet counts.

Dependencies and integration: depends on Linux flow dissector/action APIs, VCAP API/client helpers, `vcap_tc` common flower parsers, LAN966x VCAP chain layout, and driver constants such as `LAN966X_PMM_REPLACE`.

Risks: unsupported combinations must fail early with extack; otherwise rules can validate against the wrong keyset or actionset. Chain-link semantics are narrow and currently only support IS1-to-IS2 and IS1-to-ES0. Deletion loops over all rules with the same cookie, so cookie uniqueness assumptions matter. Test signals include flower matches for MAC/IP/TCP/UDP/VLAN/ARP/fragment keys, invalid ethertype/key combinations per VCAP, action duplicate and trap/pass rejection, goto chain validation, ES0 VLAN pop, stats reads, and deletion of multiple rules sharing a cookie.
