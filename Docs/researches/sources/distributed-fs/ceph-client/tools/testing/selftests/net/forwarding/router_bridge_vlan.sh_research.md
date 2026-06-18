# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_vlan.sh

Purpose: validates an 802.1Q bridge used as an L3 router interface for multiple VLANs, with VLAN 555 initially the bridge PVID and VLAN 777 later selected as the PVID. It confirms that changing bridge self VLAN membership affects expected routed connectivity.

Key functions are `config_555`, `config_777`, `vlan`, `ping_ipv4`, `ping_ipv6`, `ping_ipv4_fails`, `ping_ipv6_fails`, and VLAN-specific ping helpers for VLAN 777. `router_create` disables the default PVID, adds bridge self VLAN 555 as `pvid untagged`, adds switch-port VLANs 555/777, and assigns two L3 address pairs to `br1`; `$swp2` carries two routed destination subnets.

Control flow sets up host VLAN uppers, confirms VLAN 555 connectivity, verifies non-PVID self VLAN add/delete operations, switches the bridge PVID to 777, expects VLAN 555 failures and VLAN 777 success, then restores 555. State is Linux bridge VLAN filtering, VLAN uppers, routes, and forwarding. Risks include self VLAN/PVID edge semantics and tests relying on immediate bridge VLAN table propagation. Test signals include positive and negative ping helpers plus `check_err` validation that non-PVID bridge self VLAN add/delete succeeds.
