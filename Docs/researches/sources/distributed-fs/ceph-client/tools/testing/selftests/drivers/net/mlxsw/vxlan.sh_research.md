<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh

Purpose: large mlxsw VXLAN offload suite covering configuration sanitization and offload indication for bridge FDB entries, decap routes, replay/cleanup, and VLAN-aware VNI mapping.

Important functions/APIs: configurable environment (`ADDR_FAMILY`, `LOCAL_IP_*`, `PREFIX_LEN`, checksum flags, multicast IP); sanitization helpers for single and multiple VXLAN devices; offload setup/destroy; FDB tests; decap-route tests; join-order tests; VLAN-aware sanitization/offload tests. Uses `ip link`, `bridge fdb`, `bridge vlan`, `busywait wait_for_offload`, `grep_bridge_fdb`, and common forwarding `lib.sh`.

Control flow: setup brings two switch ports up. Sanitization tests create valid/invalid bridge+VXLAN combinations and assert attach success/failure. Offload tests build VXLAN bridges, add FDB entries, wait for offload flags, remove/re-add entries from bridge or VXLAN layers, toggle device/route/port/bridge state, and verify decap route offload tracks active VXLAN presence. VLAN-aware tests verify one VNI per VLAN and offload under tagged/pvid mappings.

State/dependencies: many temporary bridges, VXLAN devices, FDB entries, loopback local routes, and port masters. Risks include extensive mutation, offload wait timing, extant local addresses, extack/offload flag format changes, and wrapper overrides for IPv6. Test signals are command success/failure, offload flag presence/absence, and bridge/VXLAN FDB state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan.sh -->
