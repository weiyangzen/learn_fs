<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh

Purpose: RED/ECN/qevent test front-end for a single RED qdisc directly under the shaped root, rather than under ETS/PRIO bands.

Important functions/APIs: sources `sch_red_core.sh`; defines root-level `install_qdisc`, `uninstall_qdisc`, and wrappers for ECN, per-band ECN, ECN nodrop, RED drop, multicast backlog, and early-drop mirror tests.

Control flow: setup is inherited from the core. Each test attaches one RED qdisc to `$swp3 parent 1:` with a fixed backlog threshold, runs the common behavioral helper on VLAN 10, and deletes the qdisc through `defer`.

State/dependencies: qdisc state is narrower than the ETS/PRIO variants. It still depends on core traffic shaping, counters, and shared-buffer setup. Risks include RED threshold rounding and backlog build failures under hardware load. Test signals are ECN marking/non-marking, RED early drop, MC backlog visibility, and qevent mirror packet counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_root.sh -->
