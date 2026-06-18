<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh

Purpose: Spectrum-1 target provider for RIF MAC profile scale testing.

Important functions/APIs: sources `../rif_mac_profile_scale.sh`; defines `rif_mac_profile_get_target` from `devlink_resource_size_get rif_mac_profiles`.

Control flow: returns normal or overflow target based on capacity.

State/dependencies: stateless wrapper whose values can change with resource partitioning. Risks are resource occupancy and schema changes. Test signals are inherited RIF MAC profile allocation/offload/overflow outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_mac_profile_scale.sh -->
