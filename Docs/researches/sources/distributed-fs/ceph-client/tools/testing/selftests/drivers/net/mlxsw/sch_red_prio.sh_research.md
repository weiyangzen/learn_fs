<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh

Purpose: thin wrapper that reruns the ETS RED/WRED suite with a PRIO root qdisc instead of ETS, covering the alternative mlxsw offloaded classful parent.

Important functions/APIs: sets `QDISC=prio` and sources `sch_red_ets.sh`, inheriting all install/uninstall/test routines from that file and all topology helpers from `sch_red_core.sh`.

Control flow: shell variable override occurs before sourcing, so `install_root_qdisc` in the sourced file uses `prio bands 8 priomap ...` while keeping the same RED children and tests.

State/dependencies: no additional state beyond the sourced suite. The main risk is that this wrapper's behavior is implicit and depends on source order. Test signals are identical to `sch_red_ets.sh` but indicate PRIO parent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_red_prio.sh -->
