<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh

Purpose: Spectrum-2 target provider for physical port scale resource tests.

Important functions/APIs: sources `../port_scale.sh`; defines `port_get_target` from `devlink_resource_size_get physical_ports`.

Control flow: returns physical port resource capacity or capacity plus one depending on overflow mode.

State/dependencies: no local state; depends on shared generic `port_*` hooks. Risks are hotplug/resource differences and prior test occupancy. Test signals come from generic port scale setup and overflow verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/port_scale.sh -->
