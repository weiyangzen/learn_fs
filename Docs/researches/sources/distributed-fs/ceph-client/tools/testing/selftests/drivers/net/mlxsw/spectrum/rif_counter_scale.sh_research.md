<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh

Purpose: Spectrum-1 target provider for RIF counter scale testing.

Important functions/APIs: sources `../rif_counter_scale.sh`; defines `rif_counter_get_target` using RIF and RIF-counter devlink resources.

Control flow: subtracts current RIF occupancy, converts counter slots to RIF count by dividing by 20, skips impossible overflow when counters outnumber RIFs, and returns target or target plus one.

State/dependencies: stateless wrapper, but target depends on live devlink occupancy and active KVD profile. Risks include stale slot-cost assumptions and profile-dependent capacity. Test signals are inherited RIF/counter scale and overflow checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/rif_counter_scale.sh -->
