
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/lib.sh

Purpose: Core shell harness for forwarding selftests. It provides interface discovery/creation, environment validation, VRF/VLAN/tunnel helpers, sysctl save/restore, packet generation/capture helpers, multicast helpers, and test result aggregation.

Important APIs/functions: `NETIFS`, `require_command` integration, `vrf_prepare/cleanup`, `vrf_create/destroy`, `simple_if_init/fini`, `tunnel_create/destroy`, `vlan_create/destroy`, `team_create/destroy`, stats helpers, `sysctl_set/restore`, `forwarding_enable/restore`, `ping_test`, `ping6_test`, `tests_run`, `check_err` family from parent lib, tcpdump helpers, multicast packet builders, and `multipath_eval`.

Control flow: on source, it loads config, validates root/tools/interfaces, optionally creates veth pairs or driver-conformant remote mappings, then defines helpers. Importing tests define `NUM_NETIFS` and `ALL_TESTS`, perform setup, call `setup_wait`, and invoke `tests_run`.

State/persistence: can create veths, VRFs, VLANs, tunnels, team devices, qdiscs, filters, tcpdump temp files, sysctl snapshots, MAC snapshots, and multicast daemons via helper calls. Most state is restored by explicit test cleanup.

Dependencies/integration: imports `tools/testing/selftests/net/lib.sh`, uses `ip`, `tc`, `jq`, `ethtool`, `mausezahn`, `tcpdump`, `teamd`, `mtools`, `smcrouted`, and kselftest status variables.

Risks: sourcing has side effects such as creating interfaces and exiting on missing prerequisites. Global arrays (`SYSCTL_ORIG`, `MTU_ORIG`, `TARGETS`) and shared `RET`/`EXIT_STATUS` are mutable. Cleanup correctness depends on caller discipline.

Test signals: helpers log pass/fail/skip/xfail through kselftest conventions; this file itself is covered by `lib_sh_test.sh`.
