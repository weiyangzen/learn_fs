<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh

Purpose: mlxsw-specific wrapper for the generic root TBF qdisc offload selftest.

Important functions/APIs: defines `sch_tbf_pre_hook`, sets `TCFLAGS=skip_sw`, and sources forwarding `sch_tbf_root.sh`.

Control flow: local code only prepares environment constraints; the sourced generic test creates the root TBF and validates rate behavior/offload.

State/dependencies: qdisc state is managed by the generic test. It depends on mlxsw qdisc offload, iproute2 TBF support, and no lldpad DCB management. Risks are source-order coupling and failures caused by non-test qdisc state. Test signals are generic root TBF pass/fail logs under `skip_sw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sch_tbf_root.sh -->
