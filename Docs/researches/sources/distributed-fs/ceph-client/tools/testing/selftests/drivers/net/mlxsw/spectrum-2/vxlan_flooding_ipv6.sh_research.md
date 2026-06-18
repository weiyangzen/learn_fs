<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh

Purpose: Spectrum-2 IPv6 VXLAN flooding test for flood record linked-list handling where each record stores four remote VTEP IPv6 addresses.

Important functions/APIs: topology helpers `h1_create`, `switch_create`, `router1_create`, `router2_create`, `setup_prepare`, `cleanup`; flooding helpers `flooding_remotes_add`, `flooding_filters_add`, `flooding_filters_del`, `flooding_check_packets`, and `flooding_test`. It uses bridge FDB append/delete on `vxlan0`, IPv6 routes, tc flower counters on `$rp2`, and mausezahn.

Control flow: creates a bridge with `vxlan0`, local loopback VTEP address, underlay routing, and 16 remote flood entries. It sends BUM traffic, then deletes middle, first, last, and single entries while expected packet-count arrays track which remotes should receive each flood.

State/dependencies: state includes bridge/VXLAN devices, loopback IPv6 address, route, tc qdiscs/filters, and FDB flood entries. Risks include cleanup after partial FDB deletion, tc counter noise, and exact record-size assumptions tied to Spectrum-2. Test signals are tc packet counters for each remote after every deletion stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/vxlan_flooding_ipv6.sh -->
