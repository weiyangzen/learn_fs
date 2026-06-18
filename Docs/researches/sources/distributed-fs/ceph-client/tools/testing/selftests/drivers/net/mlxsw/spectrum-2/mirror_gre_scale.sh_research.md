<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh

Purpose: Spectrum-2 resource-scale target provider for the generic mlxsw mirror GRE scale test.

Important functions/APIs: sources `../mirror_gre_scale.sh` and overrides `mirror_gre_get_target`. It queries `devlink_resource_size_get span_agents`.

Control flow: when `should_fail=0`, returns the supported span agent count; when `should_fail=1`, returns one more than capacity so the parent scale harness can assert graceful overflow failure.

State/dependencies: no local state. Depends on the shared scale test contract and devlink resource naming. Risks are stale resource names or capacity affected by prior tests. Test signals are inherited from the sourced mirror GRE scale setup, insertion, overflow, cleanup, and optional traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/mirror_gre_scale.sh -->
