<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh

Purpose: shared RED/WRED/ECN qdisc test core for mlxsw. It builds a multi-port, multi-VLAN topology that can intentionally create controlled backlog on `$swp3`, then supplies helpers for root RED and RED-under-ETS/PRIO tests.

Important functions/APIs: topology helpers `host_create`, `h1_create`, `h2_create`, `h3_create`, `switch_create`, `setup_prepare`, `ping_ipv4`; queue helpers `get_qdisc_handle`, `get_qdisc_backlog`, `get_nmarked`, `build_backlog`, `check_marking`; test helpers `do_ecn_test`, `do_ecn_test_perband`, `do_ecn_nodrop_test`, `do_red_test`, `do_mc_backlog_test`, `do_drop_mirror_test`, `do_drop_trap_test`, and `do_mark_mirror_test`. It depends on forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, mausezahn, ethtool stats, devlink traps, and tc qevents.

Control flow: setup creates hosts, VLANs 10/11, four bridges, ingress/egress VLAN priority maps, TBF bottlenecks, and adjusted shared-buffer thresholds. Test helpers start baseline TCP/UDP traffic, incrementally inject packets until backlog crosses a target, then verify marking, early drop, qevent mirror/trap counts, or multicast backlog visibility.

State/dependencies: state is extensive but scoped through `defer` plus common cleanup. It requires real hardware timing, working traffic generation, accurate qdisc/ethtool counters, devlink trap counters, and Spectrum-version feature gates. Risks are timing sensitivity, leftover traffic after `kill`, buffer threshold calibration, and false failures from congestion variance. Test signals are backlog thresholds, packet-mark percentages, qdisc packet/mark counters, tc block stats, and devlink trap packet increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_core.sh -->
