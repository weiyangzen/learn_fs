# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_etsprio.sh

Purpose: shared driver for testing TBF beneath classful ETS or PRIO qdiscs, and classful qdiscs beneath a root TBF. It is parameterized by `QDISC` from wrappers.

Important functions are `tbf_test_one`, `tbf_test`, and `tbf_root_test`. It sources `sch_tbf_core.sh`, derives `QDISC_TYPE`, installs class-level TBF qdiscs at `10:3` and `10:2` for 400/800 Mbit measurements, and tests a root TBF with child classful qdisc and `bfifo` leaves.

Control flow starts with inherited topology setup, runs ping, installs a root ETS/PRIO qdisc with three bands, measures per-class TBF rates, then replaces root with a 400 Mbit TBF and installs ETS/PRIO below it so both VLAN streams should be capped at 400 Mbit. State is qdisc hierarchy and inherited VLAN/bridge/traffic state. Risks include qdisc syntax differences between ETS and PRIO, class ID mapping (`10:3` for VLAN 10 and `10:2` for VLAN 11), and rate tolerance on slow environments. Test signals are inherited `do_tbf_test` rate checks and log names identifying `root-$QDISC_TYPE-tbf` and `root-tbf-$QDISC_TYPE`.
