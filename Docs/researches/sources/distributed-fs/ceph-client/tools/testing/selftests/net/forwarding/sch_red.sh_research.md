# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_red.sh

Purpose: tests RED and ECN qdisc behavior under a controlled bottleneck. It verifies marking, early drop, nodrop mode, and qevents that mirror marked or dropped packets.

Key functions are `get_qdisc_backlog`, `get_nmarked`, `get_qdisc_npackets`, `get_nmirrored`, `send_packets`, `build_backlog`, `check_marking`, `check_mirroring`, `do_ecn_test`, `do_ecn_nodrop_test`, `do_red_test`, `do_red_qevent_test`, `do_ecn_qevent_test`, and `install_qdisc`. Setup creates a bridge with three switch ports, 10 Mbit TBF on H1 and `$swp3`, jumbo MTUs, and a dummy `_drop_test` mirror target.

Control flow starts steady traffic from H1, injects additional traffic from H2 to create backlog on a RED child qdisc under TBF, then samples RED counters and mirror counters. State is qdisc hierarchy, dummy link stats, bridge topology, traffic processes, and MTUs. Risks include rate/backlog calibration, slow system xfails, reliance on qdisc JSON/stat fields, and process cleanup. Test signals are backlog construction success/failure, marking percentage thresholds, early-drop behavior, and mirror counter deltas for qevents.
