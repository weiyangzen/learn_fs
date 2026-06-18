# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge.sh

Purpose: builds a two-host IPv4/IPv6 routed topology where one router-side subnet is represented by an 802.1Q-aware Linux bridge. It validates that a bridge netdevice used as an L3 router interface survives slave remastering and PVID changes.

Important functions are `h1_create`, `h2_create`, `router_create`, `config_remaster`, `config_remove_pvid`, `config_add_pvid`, `config_late_pvid`, `ping_ipv4`, and `ping_ipv6`. The script depends on `lib.sh` for `simple_if_init`, `vrf_prepare`, `__addr_add_del`, ping helpers, and cleanup trapping. Control flow assigns four `NETIFS`, creates host VRFs and routes, creates `br1` with `vlan_filtering 1`, enslaves `$swp1`, assigns L3 addresses to `br1` and `$swp2`, enables forwarding, runs `ALL_TESTS`, and unwinds in reverse.

State is kernel networking state only: VRFs, bridge, addresses, routes, forwarding sysctls, and bridge VLAN table entries. Risks include bridge PVID semantics changing when the default VLAN is removed or restored, stale master relationships after failure, and timing sensitivity around `sleep 2`. Test signals are successful pings before/after remastering, expected ping failures after removing the bridge PVID, and restored connectivity after re-adding or late-adding PVID.
