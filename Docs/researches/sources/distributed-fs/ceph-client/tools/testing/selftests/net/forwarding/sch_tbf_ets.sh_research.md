# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_ets.sh

Purpose: thin driver selecting ETS as the parent qdisc for shared TBF-under-class tests. It sets `QDISC="ets strict"` and sources `sch_tbf_etsprio.sh`.

There are no local functions. All setup, traffic generation, qdisc installation, and assertions are inherited from `sch_tbf_core.sh` and `sch_tbf_etsprio.sh`. The important integration contract is the `QDISC` shell variable: `sch_tbf_etsprio.sh` expands it into `tc qdisc ... $QDISC 3 priomap 2 1 0`, producing an ETS qdisc with strict bands.

Control flow is entirely delegated to the sourced script, which eventually runs `setup_prepare`, `setup_wait`, and `tests_run`. State and cleanup are also delegated. Risks are that a change in the shared script could break this wrapper silently, and ETS syntax support is required in `tc`/kernel. Test signals are inherited: ping, per-class TBF rates for VLAN 10 and 11, and root-TBF-under-ETS behavior.
