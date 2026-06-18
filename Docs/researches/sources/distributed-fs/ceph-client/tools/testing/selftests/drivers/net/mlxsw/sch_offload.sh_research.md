<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh

Purpose: validates qdisc offload indication for root and nested qdisc combinations on mlxsw, especially legal and illegal trees involving ETS/PRIO containers, RED/TBF leaves, FIFO leaves, and unsupported DRR.

Important functions/APIs: `check_not_offloaded`, `check_all_offloaded`, `with_ets`, `with_prio`, `with_red`, `with_tbf`, `with_pfifo`, `with_bfifo`, `with_drr`, recursive `with_qdiscs`, `do_test_combinations`, `test_root`, `test_port_tbf`, `test_etsprio`, and `test_etsprio_port_tbf`. It uses `tc qdisc`, `tc q sh ... invisible`, and `qdisc_stats_get`.

Control flow: recursive helpers build temporary qdisc trees, execute either an offload or no-offload checker at the leaf, then unwind by deleting qdiscs. The combinator covers allowed single RED/TBF chains and rejects duplicated RED/TBF or DRR combinations. `test_port_tbf` tests parent offload under a port-level TBF and ETS/PRIO parent.

State/dependencies: only qdisc state on one interface is persistent during each subtest; `cleanup` calls `pre_cleanup`. Requires qdisc JSON/offload visibility from iproute2 and mlxsw qdisc offload support. Risks include fragile parsing of `tc q sh dev ... invisible`, recursive cleanup if a nested creation fails, and evolving offload semantics. Test signals are per-combination `log_test` results and `.offloaded` booleans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_offload.sh -->
