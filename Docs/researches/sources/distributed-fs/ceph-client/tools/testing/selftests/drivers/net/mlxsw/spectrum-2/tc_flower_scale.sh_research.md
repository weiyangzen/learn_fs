<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh

Purpose: Spectrum-2 target provider for generic flower rule scale testing, bounded by available flow counters.

Important functions/APIs: sources `../tc_flower_scale.sh`; defines `tc_flower_get_target`; queries `devlink_resource_size_get counters flow` and `devlink_resource_occ_get counters flow`.

Control flow: subtracts existing flow counter occupancy, divides by two because each rule uses packet and byte counters, then returns target or target plus one for overflow.

State/dependencies: reads devlink counter state. Risks are counter accounting changes, background counter occupancy, and overflow target exceeding other resources first. Test signals are inherited batch insertion, `in_hw` counts, and traffic checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum-2/tc_flower_scale.sh -->
