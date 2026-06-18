<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh

Purpose: broad mlxsw rtnetlink regression suite for interface, bridge, VLAN, LAG, neighbor, nexthop, nexthop-object, locked-port, and devlink reload scenarios. It validates that valid kernel networking configurations succeed, unsupported configurations fail with no driver warnings, and mlxsw RIF/FDB/offload reference state is not leaked.

Important functions/APIs: `setup_prepare`, `cleanup`, and `ALL_TESTS` integrate with forwarding `lib.sh`; `devlink_reload` comes from `devlink_lib.sh`. Test bodies exercise `ip link`, `ip address`, `bridge vlan`, `bridge fdb`, `ip neigh`, `ip nexthop`, route installation, LAG creation, VLAN upper stacking, locked bridge ports, and offload checks through `wait_for_offload`, `busywait`, `check_err`, `check_fail`, and `log_test`.

Control flow: the harness reserves two netifs, brings both ports up, runs each named scenario, and tears the ports down. Tests create temporary bridges, VLAN devices, VRFs, LAGs, nexthops, and routes, then delete or mutate them to trigger previous bug paths such as RIF deletion, duplicate VLAN rejection, nexthop object updates, and devlink reload cleanup.

State/dependencies: persistent state is only kernel networking state; cleanup is local to each test plus global `pre_cleanup`. Requires real mlxsw-capable ports, iproute2 with nexthop support, bridge/vlan/vrf modules, and devlink. Risks are high around incomplete cleanup after failed mid-test mutations, timing of offload indication, and extack/message matching. Test signals are ksft-style `log_test` outcomes and absence of kernel traces or reload failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/rtnetlink.sh -->
