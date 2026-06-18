<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh

Purpose: Spectrum-2 target provider for generic RIF MAC profile scale testing.

Important functions/APIs: sources `../rif_mac_profile_scale.sh`; defines `rif_mac_profile_get_target` from `devlink_resource_size_get rif_mac_profiles`.

Control flow: returns capacity for success mode and capacity plus one for overflow mode.

State/dependencies: stateless wrapper. Risks are resource name changes or nonzero occupancy outside the test. Test signals are inherited from RIF MAC profile setup/test/cleanup hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_mac_profile_scale.sh -->
