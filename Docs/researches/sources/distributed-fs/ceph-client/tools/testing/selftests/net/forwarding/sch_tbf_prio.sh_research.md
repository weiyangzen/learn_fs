# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_prio.sh

Purpose: thin wrapper selecting PRIO as the classful qdisc for the shared TBF class tests. It sets `QDISC="prio bands"` and sources `sch_tbf_etsprio.sh`.

The file has no local functions or cleanup. Its only API surface is the `QDISC` variable, which causes the shared script to create a `prio bands 3 priomap 2 1 0` qdisc. All topology, qdisc layering, traffic generation, and assertions come from `sch_tbf_core.sh` and `sch_tbf_etsprio.sh`.

Control flow is delegated at source time to the shared script, which handles optional `sch_tbf_pre_hook`, setup, wait, test execution, and exit status. State is inherited qdisc/bridge/VLAN state. Risks are wrapper fragility if shared scripts assume ETS-only behavior, class ID mapping mismatches, and kernel/tc support for PRIO class hierarchy. Test signals are ping success, 400/800 Mbit per-band TBF rates under PRIO, and 400 Mbit root TBF behavior for both streams.
