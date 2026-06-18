<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh

Purpose: tests mlxsw veto/rollback paths for unsupported VXLAN FDB entries and VXLAN changelink parameters.

Important functions/APIs: env variables for local/remote IPs, checksum flags, and multicast IP; `setup_prepare`, `cleanup`, `fdb_create_veto_test`, `fdb_replace_veto_test`, `fdb_append_veto_test`, `fdb_changelink_veto_test`.

Control flow: creates a bridge with one physical port and a VXLAN device, then verifies multicast MAC, explicit UDP port on replace/append, and multicast-group changelink are rejected and include `mlxsw_spectrum` extack. Valid baseline FDB entries are added before replace/append negative checks.

State/dependencies: bridge, VXLAN, port state, FDB entries. Risks are extack text matching, rollback correctness after failed operations, and wrapper-provided IPv6 parameter differences. Test signals are expected failures plus extack presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/vxlan_fdb_veto.sh -->
