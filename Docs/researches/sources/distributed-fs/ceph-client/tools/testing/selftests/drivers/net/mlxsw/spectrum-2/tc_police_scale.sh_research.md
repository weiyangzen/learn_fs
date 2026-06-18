<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh

Purpose: Spectrum-2 target provider for generic tc police scale testing.

Important functions/APIs: sources `../tc_police_scale.sh`; defines `tc_police_get_target` from `devlink_resource_size_get global_policers single_rate_policers`.

Control flow: returns exact policer capacity for normal mode and capacity plus one for overflow mode.

State/dependencies: stateless except for devlink resource reads. Risks include shared policer occupancy and resource naming changes. Test signals are inherited police rule offload count and overflow failure checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_police_scale.sh -->
