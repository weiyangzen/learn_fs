<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh

Purpose: generic mlxsw scale-test module for offloaded tc police actions, sourced by resource-scale runners.

Important functions/APIs: `TC_POLICE_NUM_NETIFS`, setup/cleanup hooks, `tc_police_addr`, `tc_police_rules_create`, `__tc_police_test`, and `tc_police_test`.

Control flow: initializes one host and one switch port, writes a temporary tc batch containing IPv6 flower rules with police actions, executes it, and verifies JSON offload count equals the requested count unless overflow was expected.

State/dependencies: batch file, clsact qdisc, police actions, VRF state. Risks include no explicit batch-file removal in local cleanup, high rule counts, parsing `.options.in_hw`, and policer resource sharing changes. Test signals are tc batch insertion and offloaded filter count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_scale.sh -->
