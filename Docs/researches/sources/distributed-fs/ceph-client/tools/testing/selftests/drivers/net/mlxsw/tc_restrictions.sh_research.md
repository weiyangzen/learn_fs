<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh

Purpose: negative/positive suite for mlxsw tc offload restrictions around shared blocks, mirred redirect/mirror, matchall sampling, protocol matching, and police limits.

Important functions/APIs: tests include `shared_block_drop_test`, `egress_redirect_test`, `multi_mirror_test`, `matchall_sample_egress_test`, ingress/egress matchall-behind-flower helpers, `matchall_proto_match_test`, `police_limits_test`, and `multi_police_test`. It uses forwarding `tc_common.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, `check_tc_shblock_support`, and `mlxsw_only_on_spectrum`.

Control flow: each test builds minimal clsact/shared-block state on two switch ports, verifies allowed configurations first, then attempts unsupported combinations expecting `check_fail`, and cleans qdiscs/filters inline.

State/dependencies: temporary tc qdiscs, shared blocks, filters, police and mirror actions. Risks are extant shared block IDs, spectrum-specific skips, and cleanup ordering when a negative step unexpectedly succeeds. Test signals are exact success/failure of tc commands for each restriction boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_restrictions.sh -->
