<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh

Purpose: RED/WRED test front-end that installs RED leaf qdiscs under an ETS root qdisc, using `sch_red_core.sh` for topology and behavioral checks.

Important functions/APIs: defines `ALL_TESTS`, `QDISC=ets` by default, `install_root_qdisc`, `install_qdisc_tc0`, `install_qdisc_tc1`, `install_qdisc`, uninstall variants, and test wrappers `ecn_test`, `ecn_test_perband`, `ecn_nodrop_test`, `red_test`, `mc_backlog_test`, `red_mirror_test`, `red_trap_test`, `ecn_mirror_test`.

Control flow: installs an ETS root at parent `1:` on `$swp3`, then attaches RED instances to TC0 and TC1 bands with distinct backlog thresholds. Each wrapper defers uninstall and calls common core routines for ECN, RED drop, multicast backlog, and qevent behavior. It blocks execution if lldpad may be managing DCB.

State/dependencies: persistent state is temporary qdisc hierarchy and tc block qevents. It relies on precise per-band mapping from VLAN priority to mlxsw traffic classes. Risks include mis-mapped bands, qdisc counter latency, and qevent support variation. Test signals are per-TC backlog, ECN mark, early drop, mirror, trap, and multicast backlog outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_ets.sh -->
