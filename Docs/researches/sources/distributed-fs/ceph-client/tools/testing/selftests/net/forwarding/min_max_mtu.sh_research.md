
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/min_max_mtu.sh

Purpose: Tests device-reported minimum and maximum MTU constraints and traffic behavior at those limits through VLAN interfaces.

Important APIs/functions: topology helpers `h1_create`, `switch_create`; tests `ping_ipv4`, `ping_ipv6`, `max_mtu_config_test`, `max_mtu_traffic_test`, `min_mtu_config_test`, `min_mtu_traffic_test`; helpers `min_max_mtu_get_if`, `ensure_compatible_min_max_mtu`, `mtu_set_if`, `mtu_set_all_if`, `mtu_restore_all_if`, `mtu_test_ping4`, `mtu_test_ping6`.

Control flow: creates H1 VLAN 10 and switch VLAN 10, validates baseline IPv4/IPv6 pings, then for each netif tries exact min/max MTU and one out-of-range value. Traffic tests set all base and VLAN devices to shared min/max values and send no-fragment pings sized to the MTU.

State/persistence: creates one VRF, VLANs on both links, forwarding sysctls, and saves/restores MTU values through `MTU_ORIG`.

Dependencies/integration: depends on `ip -d -j link show` exposing `min_mtu`/`max_mtu`, `jq`, ping/ping6, and `lib.sh` MTU helpers.

Risks: incompatible min/max MTUs across the two interfaces produce xfail for traffic tests. IPv6 minimum MTU is intentionally not tested at min because IPv6 requires a higher floor. The script uses `ip li` abbreviation, accepted by iproute2.

Test signals: exact min/max MTU configuration succeeds, out-of-range fails, and pings sized to the configured limit pass or fail as expected.
