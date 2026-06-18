<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh

Purpose: Spectrum-2 target provider for RIF counter scale testing, selecting the limiting resource between available RIFs and counter slots.

Important functions/APIs: sources `../rif_counter_scale.sh`; defines `rif_counter_get_target`; queries `devlink_resource_size_get rifs`, `devlink_resource_size_get counters rif`, and `devlink_resource_occ_get rifs`.

Control flow: subtracts existing RIF occupancy, divides counter capacity by 20 because ingress and egress counters use 10 KVD slots each, skips overflow if counters exceed RIF capacity, then returns target or target plus one.

State/dependencies: reads but does not locally mutate devlink state. Risks are incorrect accounting if counter slot cost changes, existing RIF occupancy from environment, and overflow skip hiding a class of failures. Test signals are inherited RIF creation/counter attachment and overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/rif_counter_scale.sh -->
