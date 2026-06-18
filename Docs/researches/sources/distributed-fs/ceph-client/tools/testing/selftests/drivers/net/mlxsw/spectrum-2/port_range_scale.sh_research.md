<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh

Purpose: Spectrum-2 target provider for generic port-range register scale testing.

Important functions/APIs: sources `../port_range_scale.sh`; defines `port_range_get_target` using `devlink_resource_size_get port_range_registers`.

Control flow: returns exact capacity for normal scale run and capacity plus one for overflow run.

State/dependencies: stateless wrapper tied to devlink resource availability. Risks are shared occupancy from earlier tests and resource name drift. Test signals are inherited offload counts and overflow rejection from the generic port-range scale test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_range_scale.sh -->
