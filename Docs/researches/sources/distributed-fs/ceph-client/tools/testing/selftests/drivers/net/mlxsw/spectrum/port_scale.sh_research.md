<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh

Purpose: Spectrum-1 target provider for physical port scale tests.

Important functions/APIs: sources `../port_scale.sh`; defines `port_get_target` from `devlink_resource_size_get physical_ports`.

Control flow: returns exact capacity or capacity plus one for overflow.

State/dependencies: no local state. Risks are hardware-specific port resource reporting and prior occupancy. Test signals are inherited physical port scale/overflow outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/port_scale.sh -->
