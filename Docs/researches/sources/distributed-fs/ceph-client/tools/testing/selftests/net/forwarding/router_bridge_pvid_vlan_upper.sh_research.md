# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_pvid_vlan_upper.sh

Purpose: checks that creating and deleting a VLAN upper on a bridge for the bridge PVID VLAN does not disturb L3 routing through the bridge itself. H1 is on VLAN 10, `br1` is an 802.1Q bridge with VLAN 10 as PVID, and H2 is routed through `$swp2`.

Important functions are `h1_create`, `h2_create`, `router_create`, `shuffle_pvid`, and ping tests. The script uses `vlan_create`, `bridge vlan add`, `__addr_add_del`, VRF helpers, and forwarding helpers from `lib.sh`.

Control flow creates H1 VLAN 10, creates `br1` with `vlan_filtering 1 vlan_default_pvid 0`, assigns L3 addresses directly to `br1`, marks VLAN 10 `pvid untagged self`, then runs connectivity, creates `br1.10` with an arbitrary address, deletes it, and checks connectivity again. State is temporary bridge/VLAN/address/route state. Risks include bridge self-PVID behavior changing when a VLAN upper is present and address ownership ambiguity between `br1` and `br1.10`. Test signals are IPv4 and IPv6 pings before and after `shuffle_pvid`.
