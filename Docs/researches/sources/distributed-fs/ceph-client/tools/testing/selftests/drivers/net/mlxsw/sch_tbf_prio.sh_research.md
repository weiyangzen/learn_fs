<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh

Purpose: mlxsw-specific wrapper for the generic TBF-under-PRIO selftest.

Important functions/APIs: provides `sch_tbf_pre_hook`, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_prio.sh`.

Control flow: delegated generic test runs after the hook prevents external DCB ownership conflicts. Hardware-only execution is requested through `skip_sw`.

State/dependencies: no local persistent state; the sourced script owns qdisc and traffic setup. Risks mirror the ETS wrapper: implicit source-time contract and environmental DCB interference. Test signals are generic TBF PRIO assertions executed against mlxsw offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_prio.sh -->
