# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets_core.sh

Purpose: common topology and qdisc-control layer for ETS scheduler tests. It builds three VLAN streams, bridge forwarding between `$swp1` and `$swp2`, and provides callbacks used by `sch_ets_tests.sh`.

Important functions are `sip`, `dip`, `ets_start_traffic`, `priomap_mode`, `classifier_mode`, `ets_change_qdisc_priomap`, `ets_change_qdisc_classifier`, `ets_delete_qdisc`, `h1_create`, `h2_create`, `ets_switch_create`, `setup_prepare`, `ping_ipv4`, and `ets_run`. It sources `lib.sh` and `sch_ets_tests.sh`, sets `PARENT` and `QDISC_DEV`, and uses `defer` heavily for cleanup.

Control flow creates VLANs 10-12 on H1/H2 and switch ports, maps egress/ingress 802.1p priorities, creates one bridge per VLAN, then test modes install ETS either with priomap or with `basic` classifier filters mapping meta priorities to ETS classes. State is VLAN interfaces, bridge devices, qdisc/classifier state, MTU changes, and background traffic processes. Risks include deferred cleanup dependency, qdisc mode global `ETS_CHANGE_QDISC`, and needing overcommitment from the driver. Test signals are ping success per VLAN and scheduler ratio assertions supplied by `sch_ets_tests.sh`.
