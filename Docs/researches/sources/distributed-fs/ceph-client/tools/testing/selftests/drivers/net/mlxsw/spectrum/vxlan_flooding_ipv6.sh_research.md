<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh

Purpose: Spectrum-1 IPv6 VXLAN flooding test for flood records containing five remote VTEP IPv6 addresses per record.

Important functions/APIs: defines the same topology and helper set as the Spectrum-2 variant: host/router/switch setup, FDB remote insertion, tc filter counters, deletion stages, and packet checking.

Control flow: creates 20 remote VTEPs, sends one flood packet, then deletes a middle record, first record, last record, and individual entries from a remaining record, updating expected packet arrays after each stage.

State/dependencies: bridge, VXLAN, loopback IPv6, route, FDB, and tc filter state. Risks include exact record-size assumptions, IPv6 route/offload timing, and noisy counters. Test signals are per-remote packet counts after each flood stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/vxlan_flooding_ipv6.sh -->
