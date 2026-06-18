<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh

Purpose: Spectrum-1 router scale target provider that sizes route stress from the `kvd/hash_single` partition.

Important functions/APIs: sources `../router_scale.sh`; defines `router_get_target` using `devlink_resource_size_get kvd hash_single`.

Control flow: returns 85 percent of hash-single capacity in normal mode and capacity plus one in overflow mode.

State/dependencies: stateless wrapper but capacity depends on current KVD profile. Risks include heuristic mismatch and profile-induced target variation. Test signals are inherited route programming, offload, traffic, and overflow logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/router_scale.sh -->
