<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh

Purpose: Spectrum-1 target provider for generic port range register scale testing.

Important functions/APIs: sources `../port_range_scale.sh`; defines `port_range_get_target` using `devlink_resource_size_get port_range_registers`.

Control flow: returns capacity or capacity plus one for overflow.

State/dependencies: stateless except devlink reads. Risks are occupancy/resource layout changes under different KVD profiles. Test signals are inherited from generic port range scale checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_range_scale.sh -->
