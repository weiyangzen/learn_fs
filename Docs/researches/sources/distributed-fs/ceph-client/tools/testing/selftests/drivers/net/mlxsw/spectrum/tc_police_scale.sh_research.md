<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh

Purpose: Spectrum-1 target provider for generic single-rate policer scale testing.

Important functions/APIs: sources `../tc_police_scale.sh`; defines `tc_police_get_target` from `global_policers/single_rate_policers`.

Control flow: returns exact capacity or capacity plus one for overflow.

State/dependencies: stateless wrapper around devlink reads. Risks are existing policer occupancy and resource schema changes. Test signals are inherited policer insertion/offload-count/overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/tc_police_scale.sh -->
