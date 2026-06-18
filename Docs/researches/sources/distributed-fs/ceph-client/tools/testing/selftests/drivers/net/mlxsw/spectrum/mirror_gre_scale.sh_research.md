<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh

Purpose: Spectrum-1 target provider for generic mirror GRE scale testing.

Important functions/APIs: sources `../mirror_gre_scale.sh`; defines `mirror_gre_get_target` from `devlink_resource_size_get span_agents`.

Control flow: normal mode returns span-agent capacity; overflow mode returns capacity plus one.

State/dependencies: stateless wrapper around generic scale hooks. Risks are resource capacity altered by KVD profile or prior tests. Test signals are inherited mirror GRE creation/offload/overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/mirror_gre_scale.sh -->
