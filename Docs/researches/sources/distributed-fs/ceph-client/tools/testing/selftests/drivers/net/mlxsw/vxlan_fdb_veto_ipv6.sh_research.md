<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh

Purpose: IPv6 wrapper for the VXLAN FDB veto suite.

Important functions/APIs: sets IPv6 `LOCAL_IP`, `REMOTE_IP_1`, `REMOTE_IP_2`, IPv6 zero-checksum flags, and multicast `MC_IP`, then sources `vxlan_fdb_veto.sh`.

Control flow: source-time variable overrides make the base veto tests create IPv6 VXLAN and remote VTEP entries.

State/dependencies: inherited entirely from the base script. Risks are implicit source contract and IPv6-specific checksum/multicast behavior. Test signals are base veto pass/fail logs under IPv6 parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto_ipv6.sh -->
