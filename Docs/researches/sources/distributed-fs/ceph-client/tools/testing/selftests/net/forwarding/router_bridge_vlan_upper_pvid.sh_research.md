# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan_upper_pvid.sh

Purpose: validates interaction between bridge self PVID settings and a VLAN upper (`br1.10`) used as the routed interface. H1 sends tagged VLAN 10 traffic, while the router side uses a bridge VLAN upper rather than an address directly on `br1`.

Key functions are `pvid_set_unset`, `pvid_set_move`, `shuffle_vlan`, and dual-stack pings. `router_create` uses `vlan_filtering 1 vlan_default_pvid 0`, adds VLAN 10 to both bridge self and `$swp1`, creates `br1.10`, and assigns router addresses there. `pvid_set_unset` toggles VLAN 10 self PVID, while `pvid_set_move` moves PVID from VLAN 10 to VLAN 20.

Control flow checks connectivity, toggles self PVID, checks again, moves PVID, and checks again. State is transient kernel bridge VLAN/PVID state plus VLAN upper and route state. Risks include accidental PVID changes altering which device receives L3 traffic, lack of assertions inside `shuffle_vlan`, and timing sensitivity from one-second sleeps. Test signals are IPv4/IPv6 pings after each PVID mutation; success means the VLAN upper remains the effective routed endpoint.
