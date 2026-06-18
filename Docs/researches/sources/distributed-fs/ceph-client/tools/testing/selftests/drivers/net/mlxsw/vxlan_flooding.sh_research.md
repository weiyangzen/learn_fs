<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh

Purpose: IPv4 VXLAN flooding correctness test for mlxsw flood records containing three remote VTEP addresses per record.

Important functions/APIs: topology helpers for host, switch bridge/VXLAN, underlay routers, setup/cleanup; flooding helpers for FDB remote insertion, tc counter filters, packet checking, and `flooding_test`.

Control flow: configures VXLAN local address on loopback, route to remote VTEPs through a router port, and 12 flood remotes. It sends BUM traffic to a dummy destination MAC, verifies all remotes get one packet, deletes middle/first/last records and individual entries, then verifies updated packet arrays.

State/dependencies: bridge/VXLAN/loopback/route/VRF state plus tc filters on router and isolation filters on host/bridge. Risks include exact record packing assumption, tc counter noise, missing cleanup on failed deletion, and route/offload timing. Test signals are per-remote tc packet counters after each flood stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_flooding.sh -->
