# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_ets.sh

Purpose: veth/slowpath driver for the shared ETS qdisc test core. It configures a TBF bottleneck so the ETS scheduler on `$swp2` must arbitrate over competing VLAN-prioritized streams.

The script sources `sch_ets_core.sh`, sets `lib_dir=.`, defines `ALL_TESTS`, implements `switch_create`, and implements the `collect_stats` callback required by `sch_ets_tests.sh`. `switch_create` calls `ets_switch_create`, then adds `tc qdisc add dev $swp2 root handle 1: tbf rate 1Gbit burst 1Mbit latency 100ms`, sets `PARENT="parent 1:"`, and defers TBF cleanup.

Control flow is delegated to `ets_run` from the core. State is qdisc hierarchy on `$swp2`, bridge/VLAN topology from the core, traffic generators started by the test library, and deferred cleanup scopes. Integration is intentionally callback-based so driver-specific offload variants can reuse the same tests. Risks are bottleneck calibration, timing on slow systems, and stats collection depending on qdisc class byte counters. Test signals come from `ping_ipv4`, priomap mode, classifier mode, strict, mixed, DWRR, and plug tests.
