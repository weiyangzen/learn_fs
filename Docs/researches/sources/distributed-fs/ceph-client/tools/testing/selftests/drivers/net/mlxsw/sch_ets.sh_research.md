<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh

Purpose: mlxsw driver adapter for the generic ETS qdisc selftest, forcing the tests through offloaded datapath behavior and buffer settings that make DWRR/strict scheduling observable.

Important functions/APIs: sources `sch_ets_core.sh` and `devlink_lib.sh`; overrides `switch_create` and `collect_stats`; calls `bail_on_lldpad` and `ets_run`. It uses `tc qdisc replace ... tbf`, ETS qdisc setup from the common core, and devlink shared-buffer helpers such as `devlink_port_pool_th_set` and `devlink_tc_bind_pool_th_set`.

Control flow: `switch_create` installs a TBF bottleneck on `$swp2`, delegates common ETS topology setup, raises ingress/egress shared-buffer thresholds, and defers restoration. `collect_stats` waits for qdisc counters to update and returns per-stream byte counters for the common ETS runner.

State/dependencies: state is qdisc configuration and devlink shared-buffer thresholds, restored through `defer`. It depends on DCB not being managed by lldpad and on mlxsw's hard-coded 1:1 802.1p priority mapping. Risks include scheduler timing, stale qdisc counters, and environmental DCB daemons. Test signals are ping success, priomap tests, and strict/mixed/DWRR byte distributions from the shared ETS core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_ets.sh -->
