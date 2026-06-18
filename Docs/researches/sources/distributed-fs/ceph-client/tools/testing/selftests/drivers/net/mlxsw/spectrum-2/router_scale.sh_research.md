<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh

Purpose: Spectrum-2 router scale target provider using total KVD size rather than the Spectrum-1 hash partition.

Important functions/APIs: sources `../router_scale.sh`; defines `router_get_target` using `devlink_resource_size_get kvd`.

Control flow: for normal mode returns 85 percent of KVD capacity to avoid exact-limit instability; for overflow mode returns capacity plus one.

State/dependencies: stateless wrapper for the generic router scale module. Risks include the 85 percent heuristic being too aggressive or too conservative on future resource layouts. Test signals are inherited route programming/offload and overflow rejection checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/router_scale.sh -->
