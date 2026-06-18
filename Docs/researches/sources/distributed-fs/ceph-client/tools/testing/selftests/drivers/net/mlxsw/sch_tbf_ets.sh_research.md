<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh

Purpose: mlxsw-specific wrapper for the generic TBF-under-ETS forwarding selftest, forcing offloaded TC setup.

Important functions/APIs: defines `sch_tbf_pre_hook` to reject lldpad-managed DCB, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_ets.sh`.

Control flow: all topology and tests are delegated to the generic forwarding script after mlxsw-specific pre-hook and tc flag setup. The hook runs before qdisc configuration.

State/dependencies: state and cleanup are owned by the sourced generic test. Depends on mlxsw offload support and a system not controlled by lldpad. Risks are implicit behavior through sourcing and mismatch with generic script changes. Test signals come from the generic TBF ETS suite with `skip_sw` enforcing hardware offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_ets.sh -->
