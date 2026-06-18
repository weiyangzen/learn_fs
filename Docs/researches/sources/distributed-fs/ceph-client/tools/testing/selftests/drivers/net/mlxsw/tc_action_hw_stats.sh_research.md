<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh

Purpose: verifies mlxsw handling of tc action `hw_stats` modes and corresponding devlink flow-counter occupancy.

Important functions/APIs: `h1_create`, `switch_create`, `hw_stats_test`, mode wrappers `default_hw_stats_test`, `immediate_hw_stats_test`, `delayed_hw_stats_test`, `disabled_hw_stats_test`, `setup_prepare`, `cleanup`, and `check_tc_action_hw_stats_support`. Uses `tc filter flower skip_sw`, `devlink_resource_get counters flow`, jq, mausezahn, and `tc_check_packets`.

Control flow: for supported modes, records flow-counter occupancy, installs a drop rule with the requested hw_stats setting, checks occupancy delta, sends one packet, verifies packet stats match expected visibility, then deletes the rule. Delayed mode is expected to be rejected.

State/dependencies: one clsact qdisc and flow counters. Risks are changed counter accounting, delayed stats support evolution, and exact occupancy deltas. Test signals are rule insertion success/failure, flow counter occupancy, and tc packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_action_hw_stats.sh -->
